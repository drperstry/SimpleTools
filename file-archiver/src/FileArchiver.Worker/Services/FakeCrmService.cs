using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace FileArchiver.Worker.Services;

public sealed class FakeCrmService : ICrmService
{
    private readonly ArchivalOptions _options;
    private readonly ILogger<FakeCrmService> _logger;

    public FakeCrmService(IOptions<ArchivalOptions> options, ILogger<FakeCrmService> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    public Task<IReadOnlyList<IncidentArchivalJob>> GetJobsAsync(CancellationToken ct)
    {
        _logger.LogInformation("[DryRun] Scanning source folder: {Root}", _options.SourceUncRoot);

        var jobs = new List<IncidentArchivalJob>();

        if (!Directory.Exists(_options.SourceUncRoot))
        {
            _logger.LogWarning("[DryRun] Source root does not exist: {Root}", _options.SourceUncRoot);
            return Task.FromResult<IReadOnlyList<IncidentArchivalJob>>(jobs);
        }

        foreach (var dir in Directory.EnumerateDirectories(_options.SourceUncRoot))
        {
            if (!Guid.TryParse(Path.GetFileName(dir), out var incidentId))
                continue;

            var files = Directory.EnumerateFiles(dir, "*", SearchOption.AllDirectories)
                .Select((f, i) => new NtwsFileRecord(
                    Id: Guid.NewGuid(),
                    IncidentId: incidentId,
                    FileName: Path.GetFileName(f),
                    FolderPath: dir,
                    IsArchived: false,
                    SizeBytes: new FileInfo(f).Length,
                    CreatedOn: DateTime.UtcNow.AddDays(-100)
                ))
                .ToList();

            if (files.Count == 0) continue;

            jobs.Add(new IncidentArchivalJob
            {
                IncidentId = incidentId,
                FolderPath = dir,
                Files = files
            });
        }

        _logger.LogInformation("[DryRun] Found {Count} incident folder(s)", jobs.Count);
        return Task.FromResult<IReadOnlyList<IncidentArchivalJob>>(jobs);
    }

    public Task BatchSetArchivedAsync(IEnumerable<Guid> fileIds, CancellationToken ct)
    {
        var ids = fileIds.ToList();
        _logger.LogInformation("[DryRun] Would set ntws_archive=true on {Count} file record(s)", ids.Count);
        return Task.CompletedTask;
    }

    public Task CreateZipFileRecordAsync(Guid incidentId, string archiveFolderPath, string zipFileName, long sizeBytes, CancellationToken ct)
    {
        _logger.LogInformation("[DryRun] Would create ntws_file record: incident={IncidentId}, zip={Zip}, path={Path}, size={Bytes:N0}",
            incidentId, zipFileName, archiveFolderPath, sizeBytes);
        return Task.CompletedTask;
    }
}
