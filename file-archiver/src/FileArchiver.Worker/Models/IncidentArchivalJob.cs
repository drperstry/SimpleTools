namespace FileArchiver.Worker.Models;

public sealed class IncidentArchivalJob
{
    public Guid IncidentId { get; init; }
    public string FolderPath { get; init; } = string.Empty;
    public List<NtwsFileRecord> Files { get; init; } = new();

    public long TotalSizeBytes => Files.Sum(f => f.SizeBytes);
    public DateTime OldestFileDate => Files.Count > 0 ? Files.Min(f => f.CreatedOn) : DateTime.MinValue;
}
