using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Newtonsoft.Json.Linq;
using System.Net;
using System.Text;

namespace FileArchiver.Worker.Services;

/// <summary>
/// Dataverse Web API implementation — same HTTP pattern as BabCrm.Crm.CrmService.
/// </summary>
public sealed class CrmService : ICrmService
{
    private const string EntityPluralName = "ntws_files";

    private readonly ICrmConfig _crmConfig;
    private readonly ArchivalOptions _options;
    private readonly ILogger<CrmService> _logger;

    public CrmService(ICrmConfig crmConfig, IOptions<ArchivalOptions> options, ILogger<CrmService> logger)
    {
        _crmConfig = crmConfig;
        _options = options.Value;
        _logger = logger;
    }

    // -------------------------------------------------------------------------
    // ICrmService
    // -------------------------------------------------------------------------

    public async Task<IReadOnlyList<IncidentArchivalJob>> GetJobsAsync(CancellationToken ct)
    {
        var sizeLimitBytes = (long)_options.FolderSizeMbThreshold * 1024 * 1024;
        var cutoff = DateTime.UtcNow.AddDays(-_options.AgeDaysThreshold);

        var allRecords = await FetchAllNonArchivedAsync(ct);

        var jobs = allRecords
            .GroupBy(r => r.IncidentId)
            .Select(g => new IncidentArchivalJob
            {
                IncidentId = g.Key,
                FolderPath = g.First().FolderPath,
                Files = g.ToList()
            })
            .Where(job => job.OldestFileDate < cutoff || job.TotalSizeBytes > sizeLimitBytes)
            .ToList();

        _logger.LogInformation("Found {Count} incidents qualifying for archival", jobs.Count);
        return jobs;
    }

    public async Task BatchSetArchivedAsync(IEnumerable<Guid> fileIds, CancellationToken ct)
    {
        var chunks = fileIds.Chunk(_options.CrmBatchSize);

        foreach (var chunk in chunks)
        {
            ct.ThrowIfCancellationRequested();
            await ExecuteChangesetAsync(chunk.Select(id => BuildArchivePatch(id)), ct);
        }
    }

    public async Task CreateZipFileRecordAsync(
        Guid incidentId,
        string archiveFolderPath,
        string zipFileName,
        long sizeBytes,
        CancellationToken ct)
    {
        var body = new JObject
        {
            ["ntws_recordid"]          = incidentId.ToString(),
            ["ntws_entitylogicalname"] = "incident",
            ["ntws_filename"]          = zipFileName,
            ["ntws_titlear"]           = zipFileName,
            ["ntws_titleen"]           = zipFileName,
            ["ntws_filepath"]          = archiveFolderPath,
            ["ntws_archive"]           = true,
            ["ntws_size"]              = (int)Math.Min(sizeBytes, int.MaxValue),
            ["ntws_published"]         = "Yes"
        };

        var result = await SaveAsync(EntityPluralName, body, ct: ct);

        if (result is null)
            throw new InvalidOperationException($"Failed to create zip file record for incident {incidentId}");

        _logger.LogInformation("Created zip file record {Id} for incident {IncidentId}",
            result["Id"], incidentId);
    }

    // -------------------------------------------------------------------------
    // Fetch helpers
    // -------------------------------------------------------------------------

    private async Task<List<NtwsFileRecord>> FetchAllNonArchivedAsync(CancellationToken ct)
    {
        var records = new List<NtwsFileRecord>();
        string? pagingCookie = null;
        int page = 1;

        while (true)
        {
            ct.ThrowIfCancellationRequested();

            var fetchXml = BuildFetchXml(pagingCookie, page);
            var requestUri = GenerateFetchXmlUrl(EntityPluralName, fetchXml);

            var (data, moreRecords, nextCookie) = await GetPageAsync(requestUri, ct);

            if (data is not null)
            {
                foreach (var token in data)
                    if (MapRecord(token) is { } r) records.Add(r);
            }

            if (!moreRecords) break;
            pagingCookie = nextCookie;
            page++;
        }

        return records;
    }

    private async Task<(JArray? data, bool moreRecords, string? pagingCookie)> GetPageAsync(
        string requestUri, CancellationToken ct)
    {
        using var client = _crmConfig.BuildClient();
        using var response = await client.GetAsync(requestUri, ct).ConfigureAwait(false);

        if (!response.IsSuccessStatusCode)
        {
            var err = await response.Content.ReadAsStringAsync(ct);
            _logger.LogError("CrmService.Get {Uri} → {Status} {Body}", requestUri, response.StatusCode, err);
            return (null, false, null);
        }

        var content = await response.Content.ReadAsStringAsync(ct);
        if (string.IsNullOrEmpty(content)) return (null, false, null);

        var obj = JObject.Parse(content);
        var data = obj["value"] is JArray arr ? arr : null;
        var more = obj["@Microsoft.Dynamics.CRM.morerecords"]?.Value<bool>() ?? false;
        var cookie = obj["@Microsoft.Dynamics.CRM.fetchxmlpagingcookie"]?.Value<string>();

        return (data, more, cookie);
    }

    // -------------------------------------------------------------------------
    // Save (POST / PATCH) — mirrors BabCrm.Crm.CrmService.Save
    // -------------------------------------------------------------------------

    private async Task<JObject?> SaveAsync(
        string entityName,
        JObject body,
        string? updateGuid = null,
        CancellationToken ct = default)
    {
        var isUpdate = !string.IsNullOrWhiteSpace(updateGuid);
        var requestUri = GeneratePostUrl(entityName) + (isUpdate ? $"({updateGuid})" : "");
        var method = isUpdate ? HttpMethod.Patch : HttpMethod.Post;

        using var request = new HttpRequestMessage(method, requestUri)
        {
            Content = new StringContent(body.ToString(), Encoding.UTF8, "application/json")
        };
        request.Headers.Add("Prefer", "return=representation");

        using var client = _crmConfig.BuildClient();
        using var response = await client.SendAsync(request, ct).ConfigureAwait(false);

        if (response.StatusCode == HttpStatusCode.NoContent || response.StatusCode == HttpStatusCode.Created ||
            response.IsSuccessStatusCode)
        {
            // Extract new record ID from OData-EntityId header when present
            if (response.Headers.TryGetValues("OData-EntityId", out var vals))
            {
                var recordUri = vals.FirstOrDefault() ?? string.Empty;
                var pre = recordUri.LastIndexOf('(');
                if (pre >= 0)
                    return JObject.FromObject(new { Id = recordUri[(pre + 1)..^1] });
            }

            var raw = await response.Content.ReadAsStringAsync(ct);
            if (!string.IsNullOrEmpty(raw))
                return JObject.Parse(raw);

            return JObject.FromObject(new { Id = updateGuid ?? string.Empty });
        }

        var errorContent = await response.Content.ReadAsStringAsync(ct);
        _logger.LogError("CrmService.Save {Uri} → {Status} {Body}", requestUri, response.StatusCode, errorContent);
        return null;
    }

    // -------------------------------------------------------------------------
    // OData $batch changeset — mirrors BabCrm.Crm.CrmService.ExecuteChangeSetBatchRequest
    // -------------------------------------------------------------------------

    private async Task ExecuteChangesetAsync(
        IEnumerable<(string url, JObject body)> operations,
        CancellationToken ct)
    {
        var batchId = $"batch_{Guid.NewGuid():N}";
        var changesetId = $"changeset_{Guid.NewGuid():N}";
        var sb = new StringBuilder();

        sb.AppendLine($"--{batchId}");
        sb.AppendLine($"Content-Type: multipart/mixed; boundary={changesetId}");
        sb.AppendLine();

        foreach (var (url, body) in operations)
        {
            sb.AppendLine($"--{changesetId}");
            sb.AppendLine("Content-Type: application/http");
            sb.AppendLine("Content-Transfer-Encoding: binary");
            sb.AppendLine();
            sb.AppendLine($"PATCH {url} HTTP/1.1");
            sb.AppendLine("Content-Type: application/json; type=entry");
            sb.AppendLine();
            sb.AppendLine(body.ToString(Newtonsoft.Json.Formatting.None));
        }

        sb.AppendLine($"--{changesetId}--");
        sb.AppendLine($"--{batchId}--");

        var batchUrl = _crmConfig.ServiceUrl.TrimEnd('/') + "/$batch";

        using var request = new HttpRequestMessage(HttpMethod.Post, batchUrl)
        {
            Content = new StringContent(sb.ToString(), Encoding.UTF8,
                $"multipart/mixed; boundary={batchId}")
        };

        using var client = _crmConfig.BuildClient();
        using var response = await client.SendAsync(request, ct).ConfigureAwait(false);

        if (!response.IsSuccessStatusCode)
        {
            var err = await response.Content.ReadAsStringAsync(ct);
            _logger.LogError("CrmService.Batch → {Status} {Body}", response.StatusCode, err);
            throw new InvalidOperationException($"Batch update failed: {response.StatusCode}");
        }
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static (string url, JObject body) BuildArchivePatch(Guid fileId)
    {
        var body = new JObject { ["ntws_archive"] = true };
        return ($"{EntityPluralName}({fileId})", body);
    }

    private static NtwsFileRecord? MapRecord(JToken token)
    {
        var incidentIdRaw = token.Value<string>("ntws_recordid");
        if (!Guid.TryParse(incidentIdRaw, out var incidentId)) return null;

        return new NtwsFileRecord(
            Id: token.Value<Guid>("ntws_fileid"),
            IncidentId: incidentId,
            FileName: token.Value<string>("ntws_filename") ?? string.Empty,
            FolderPath: token.Value<string>("ntws_filepath") ?? string.Empty,
            IsArchived: token.Value<bool>("ntws_archive"),
            SizeBytes: token.Value<long>("ntws_size"),
            CreatedOn: token.Value<DateTime>("createdon")
        );
    }

    private string GenerateFetchXmlUrl(string entityName, string fetchXml)
    {
        fetchXml = fetchXml.Replace(Environment.NewLine, "").Replace("\t", "");
        return $"{_crmConfig.ServiceUrl}{entityName}?fetchXml={Uri.EscapeDataString(fetchXml)}";
    }

    private string GeneratePostUrl(string entityName) =>
        $"{_crmConfig.ServiceUrl}{entityName}";

    private static string BuildFetchXml(string? pagingCookie, int page)
    {
        var cookieAttr = pagingCookie is not null
            ? $"paging-cookie=\"{System.Security.SecurityElement.Escape(pagingCookie)}\" page=\"{page}\""
            : $"page=\"{page}\"";

        return $"""
            <fetch count='5000' {cookieAttr} distinct='false' mapping='logical'>
              <entity name='ntws_file'>
                <attribute name='ntws_fileid' />
                <attribute name='ntws_recordid' />
                <attribute name='ntws_filename' />
                <attribute name='ntws_filepath' />
                <attribute name='ntws_size' />
                <attribute name='ntws_archive' />
                <attribute name='createdon' />
                <filter>
                  <condition attribute='ntws_archive' operator='eq' value='0' />
                  <condition attribute='ntws_entitylogicalname' operator='eq' value='incident' />
                </filter>
                <order attribute='ntws_recordid' />
              </entity>
            </fetch>
            """;
    }
}
