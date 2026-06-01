using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Helpers;
using FileArchiver.Worker.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Polly;

namespace FileArchiver.Worker.Services;

public sealed class FileArchivalService : IFileArchivalService
{
    private readonly ICrmService _crmService;
    private readonly IZipService _zipService;
    private readonly ArchivalOptions _options;
    private readonly ILogger<FileArchivalService> _logger;
    private readonly ResiliencePipeline _fileRetry;
    private readonly ResiliencePipeline _crmRetry;

    public FileArchivalService(
        ICrmService crmService,
        IZipService zipService,
        IOptions<ArchivalOptions> options,
        ILogger<FileArchivalService> logger)
    {
        _crmService = crmService;
        _zipService = zipService;
        _options = options.Value;
        _logger = logger;
        _fileRetry = RetryHelper.BuildFileRetry(_options, logger);
        _crmRetry = RetryHelper.BuildCrmRetry(_options, logger);
    }

    public async Task ArchiveIncidentAsync(IncidentArchivalJob job, CancellationToken ct)
    {
        var zipFileName = $"{job.IncidentId}.zip";
        var destinationZipPath = Path.Combine(_options.ArchiveUncPath, zipFileName);

        Directory.CreateDirectory(_options.ArchiveUncPath);

        long zipSizeBytes = 0;

        await _fileRetry.ExecuteAsync(async token =>
        {
            if (File.Exists(destinationZipPath))
            {
                _logger.LogWarning("Removing partial zip before retry: {Path}", destinationZipPath);
                File.Delete(destinationZipPath);
            }

            var progress = new Progress<string>(entry =>
                _logger.LogDebug("  Zipped: {Entry}", entry));

            zipSizeBytes = await _zipService.CreateZipAsync(job.FolderPath, destinationZipPath, progress, token);
            _logger.LogInformation("Zip created: {Path} ({Bytes:N0} bytes)", destinationZipPath, zipSizeBytes);
        }, ct);

        bool crmUpdated = false;
        await _crmRetry.ExecuteAsync(async token =>
        {
            await _crmService.BatchSetArchivedAsync(job.Files.Select(f => f.Id), token);
            await _crmService.CreateZipFileRecordAsync(job.IncidentId, _options.ArchiveUncPath, zipFileName, zipSizeBytes, token);
            crmUpdated = true;
        }, ct);

        if (_options.DeleteOriginalsAfterArchive && crmUpdated)
        {
            _logger.LogInformation("Deleting original folder: {Path}", job.FolderPath);
            Directory.Delete(job.FolderPath, recursive: true);
        }
    }
}
