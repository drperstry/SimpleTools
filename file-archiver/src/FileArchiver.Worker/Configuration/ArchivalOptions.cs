using System.ComponentModel.DataAnnotations;

namespace FileArchiver.Worker.Configuration;

public sealed class ArchivalOptions
{
    public const string SectionName = "Archival";

    [Required]
    public string CronSchedule { get; init; } = "0 2 * * *";

    [Range(1, 64)]
    public int MaxParallelism { get; init; } = 4;

    [Range(1, int.MaxValue)]
    public int AgeDaysThreshold { get; init; } = 90;

    [Range(1, int.MaxValue)]
    public int FolderSizeMbThreshold { get; init; } = 500;

    public bool DeleteOriginalsAfterArchive { get; init; } = false;

    [Required]
    public string SourceUncRoot { get; init; } = string.Empty;

    [Required]
    public string ArchiveUncPath { get; init; } = string.Empty;

    [Range(1, 10)]
    public int RetryCount { get; init; } = 3;

    [Range(1, 60)]
    public int RetryDelaySeconds { get; init; } = 5;

    [Range(1, 1000)]
    public int CrmBatchSize { get; init; } = 100;

    public bool DryRun { get; init; } = false;
}
