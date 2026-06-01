using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.PowerPlatform.Dataverse.Client;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Messages;
using Microsoft.Xrm.Sdk.Query;

namespace FileArchiver.Worker.Services;

public sealed class CrmService : ICrmService
{
    private const string EntityName = "ntws_file";
    private readonly ServiceClient _client;
    private readonly ArchivalOptions _options;
    private readonly ILogger<CrmService> _logger;

    public CrmService(ServiceClient client, IOptions<ArchivalOptions> options, ILogger<CrmService> logger)
    {
        _client = client;
        _options = options.Value;
        _logger = logger;
    }

    public async Task<IReadOnlyList<IncidentArchivalJob>> GetJobsAsync(CancellationToken ct)
    {
        var cutoff = DateTime.UtcNow.AddDays(-_options.AgeDaysThreshold);
        var sizeLimitBytes = (long)_options.FolderSizeMbThreshold * 1024 * 1024;

        var allRecords = await FetchAllNonArchivedAsync(ct);

        var groups = allRecords
            .GroupBy(r => r.IncidentId)
            .Select(g => new IncidentArchivalJob
            {
                IncidentId = g.Key,
                FolderPath = g.First().FolderPath,
                Files = g.ToList()
            })
            .Where(job =>
                job.OldestFileDate < cutoff ||
                job.TotalSizeBytes > sizeLimitBytes)
            .ToList();

        _logger.LogInformation("Found {Count} incidents qualifying for archival", groups.Count);
        return groups;
    }

    public async Task BatchSetArchivedAsync(IEnumerable<Guid> fileIds, CancellationToken ct)
    {
        var chunks = fileIds.Chunk(_options.CrmBatchSize);
        foreach (var chunk in chunks)
        {
            ct.ThrowIfCancellationRequested();

            var request = new ExecuteMultipleRequest
            {
                Settings = new ExecuteMultipleSettings
                {
                    ContinueOnError = true,
                    ReturnResponses = true
                },
                Requests = new OrganizationRequestCollection()
            };

            foreach (var id in chunk)
            {
                var entity = new Entity(EntityName, id);
                entity["ntws_archive"] = true;
                request.Requests.Add(new UpdateRequest { Target = entity });
            }

            var response = (ExecuteMultipleResponse)await Task.Run(
                () => _client.Execute(request), ct);

            var failures = response.Responses
                .Where(r => r.Fault != null)
                .ToList();

            if (failures.Count > 0)
            {
                _logger.LogWarning("{Count} CRM update(s) failed in batch", failures.Count);
                foreach (var f in failures)
                    _logger.LogWarning("  Request index {Index}: {Message}", f.RequestIndex, f.Fault.Message);

                throw new InvalidOperationException(
                    $"{failures.Count} record update(s) failed — originals will NOT be deleted.");
            }
        }
    }

    public async Task CreateZipFileRecordAsync(
        Guid incidentId,
        string archiveFolderPath,
        string zipFileName,
        long sizeBytes,
        CancellationToken ct)
    {
        var entity = new Entity(EntityName)
        {
            ["ntws_recordid"] = incidentId.ToString(),
            ["ntws_entitylogicalname"] = "incident",
            ["ntws_filename"] = zipFileName,
            ["ntws_titlear"] = zipFileName,
            ["ntws_titleen"] = zipFileName,
            ["ntws_filepath"] = archiveFolderPath,
            ["ntws_archive"] = true,
            ["ntws_size"] = (int)Math.Min(sizeBytes, int.MaxValue),
            ["ntws_published"] = "Yes"
        };

        await Task.Run(() => _client.Create(entity), ct);
        _logger.LogInformation("Created zip file record for incident {IncidentId}", incidentId);
    }

    private async Task<List<NtwsFileRecord>> FetchAllNonArchivedAsync(CancellationToken ct)
    {
        var records = new List<NtwsFileRecord>();
        string? pagingCookie = null;
        int page = 1;

        while (true)
        {
            ct.ThrowIfCancellationRequested();
            var fetchXml = BuildFetchXml(pagingCookie, page);
            var result = await Task.Run(() => _client.RetrieveMultiple(new FetchExpression(fetchXml)), ct);

            foreach (var entity in result.Entities)
            {
                var incidentIdRaw = entity.GetAttributeValue<string>("ntws_recordid");
                if (!Guid.TryParse(incidentIdRaw, out var incidentId))
                    continue;

                records.Add(new NtwsFileRecord(
                    Id: entity.Id,
                    IncidentId: incidentId,
                    FileName: entity.GetAttributeValue<string>("ntws_filename") ?? string.Empty,
                    FolderPath: entity.GetAttributeValue<string>("ntws_filepath") ?? string.Empty,
                    IsArchived: entity.GetAttributeValue<bool>("ntws_archive"),
                    SizeBytes: entity.GetAttributeValue<int>("ntws_size"),
                    CreatedOn: entity.GetAttributeValue<DateTime>("createdon")
                ));
            }

            if (!result.MoreRecords)
                break;

            pagingCookie = result.PagingCookie;
            page++;
        }

        return records;
    }

    private static string BuildFetchXml(string? pagingCookie, int page)
    {
        var cookieAttr = pagingCookie != null
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
