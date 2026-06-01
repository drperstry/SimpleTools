using FileArchiver.Worker.Models;
using FileArchiver.Worker.Services;

namespace FileArchiver.Tests.Fakes;

public sealed class FakeCrmService : ICrmService
{
    public List<IncidentArchivalJob> Jobs { get; set; } = new();
    public List<Guid> ArchivedIds { get; } = new();
    public List<(Guid IncidentId, string ZipFileName, long Size)> CreatedZipRecords { get; } = new();

    public bool ThrowOnBatchUpdate { get; set; } = false;

    public Task<IReadOnlyList<IncidentArchivalJob>> GetJobsAsync(CancellationToken ct) =>
        Task.FromResult<IReadOnlyList<IncidentArchivalJob>>(Jobs);

    public Task BatchSetArchivedAsync(IEnumerable<Guid> fileIds, CancellationToken ct)
    {
        if (ThrowOnBatchUpdate)
            throw new InvalidOperationException("Simulated CRM failure");

        ArchivedIds.AddRange(fileIds);
        return Task.CompletedTask;
    }

    public Task CreateZipFileRecordAsync(Guid incidentId, string archiveFolderPath, string zipFileName, long sizeBytes, CancellationToken ct)
    {
        CreatedZipRecords.Add((incidentId, zipFileName, sizeBytes));
        return Task.CompletedTask;
    }
}
