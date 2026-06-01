using Cronos;
using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Services;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace FileArchiver.Worker.Workers;

public sealed class ArchivalWorker : BackgroundService
{
    private readonly ICrmService _crmService;
    private readonly IFileArchivalService _archivalService;
    private readonly ArchivalOptions _options;
    private readonly ILogger<ArchivalWorker> _logger;
    private readonly bool _runNow;

    public ArchivalWorker(
        ICrmService crmService,
        IFileArchivalService archivalService,
        IOptions<ArchivalOptions> options,
        ILogger<ArchivalWorker> logger,
        IHostApplicationLifetime lifetime,
        bool runNow = false)
    {
        _crmService = crmService;
        _archivalService = archivalService;
        _options = options.Value;
        _logger = logger;
        _runNow = runNow;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        if (_runNow)
        {
            _logger.LogInformation("--run-now flag detected, executing immediately.");
            await RunArchivalCycleAsync(stoppingToken);
            return;
        }

        var cron = CronExpression.Parse(_options.CronSchedule, CronFormat.Standard);

        while (!stoppingToken.IsCancellationRequested)
        {
            var now = DateTimeOffset.UtcNow;
            var next = cron.GetNextOccurrence(now, TimeZoneInfo.Utc);
            if (next is null)
            {
                _logger.LogError("Cron expression '{Schedule}' produced no future occurrence. Stopping.", _options.CronSchedule);
                break;
            }

            var delay = next.Value - now;
            _logger.LogInformation("Next archival run scheduled at {Next:u} (in {Minutes:N0} min)", next.Value, delay.TotalMinutes);

            try
            {
                await Task.Delay(delay, stoppingToken);
            }
            catch (OperationCanceledException)
            {
                break;
            }

            await RunArchivalCycleAsync(stoppingToken);
        }
    }

    private async Task RunArchivalCycleAsync(CancellationToken ct)
    {
        _logger.LogInformation("=== Archival cycle starting ===");

        IReadOnlyList<Models.IncidentArchivalJob> jobs;
        try
        {
            jobs = await _crmService.GetJobsAsync(ct);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to fetch archival jobs from CRM. Skipping cycle.");
            return;
        }

        if (jobs.Count == 0)
        {
            _logger.LogInformation("No incidents qualify for archival.");
            return;
        }

        _logger.LogInformation("Processing {Count} incident(s) with MaxParallelism={Max}", jobs.Count, _options.MaxParallelism);

        var sem = new SemaphoreSlim(_options.MaxParallelism);
        var failedIds = new System.Collections.Concurrent.ConcurrentBag<Guid>();

        var tasks = jobs.Select(async job =>
        {
            await sem.WaitAsync(ct);
            try
            {
                await _archivalService.ArchiveIncidentAsync(job, ct);
                _logger.LogInformation("✓ Archived incident {IncidentId} ({Files} files, {Bytes:N0} bytes)",
                    job.IncidentId, job.Files.Count, job.TotalSizeBytes);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "✗ Failed to archive incident {IncidentId}", job.IncidentId);
                failedIds.Add(job.IncidentId);
            }
            finally
            {
                sem.Release();
            }
        });

        await Task.WhenAll(tasks);

        _logger.LogInformation("=== Cycle complete. Succeeded: {S}, Failed: {F} ===",
            jobs.Count - failedIds.Count, failedIds.Count);

        if (!failedIds.IsEmpty)
            await WriteDeadLetterAsync(failedIds, ct);
    }

    private static async Task WriteDeadLetterAsync(IEnumerable<Guid> ids, CancellationToken ct)
    {
        Directory.CreateDirectory("logs");
        var path = Path.Combine("logs", $"failed-{DateTime.UtcNow:yyyy-MM-dd}.jsonl");
        var lines = ids.Select(id => $"{{\"incidentId\":\"{id}\",\"failedAt\":\"{DateTime.UtcNow:o}\"}}");
        await File.AppendAllLinesAsync(path, lines, ct);
    }
}
