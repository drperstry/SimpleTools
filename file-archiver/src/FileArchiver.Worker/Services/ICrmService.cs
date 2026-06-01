using FileArchiver.Worker.Models;

namespace FileArchiver.Worker.Services;

public interface ICrmService
{
    Task<IReadOnlyList<IncidentArchivalJob>> GetJobsAsync(CancellationToken ct);

    Task BatchSetArchivedAsync(IEnumerable<Guid> fileIds, CancellationToken ct);

    Task CreateZipFileRecordAsync(
        Guid incidentId,
        string archiveFolderPath,
        string zipFileName,
        long sizeBytes,
        CancellationToken ct);
}
