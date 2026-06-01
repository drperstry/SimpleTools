using FileArchiver.Worker.Models;

namespace FileArchiver.Worker.Services;

public interface IFileArchivalService
{
    Task ArchiveIncidentAsync(IncidentArchivalJob job, CancellationToken ct);
}
