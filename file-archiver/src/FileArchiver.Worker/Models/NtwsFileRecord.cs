namespace FileArchiver.Worker.Models;

public sealed record NtwsFileRecord(
    Guid Id,
    Guid IncidentId,
    string FileName,
    string FolderPath,
    bool IsArchived,
    long SizeBytes,
    DateTime CreatedOn
);
