using System.IO.Compression;
using Microsoft.Extensions.Logging;

namespace FileArchiver.Worker.Services;

public sealed class ZipService : IZipService
{
    private const int CopyBufferSize = 81920;
    private readonly ILogger<ZipService> _logger;

    public ZipService(ILogger<ZipService> logger) => _logger = logger;

    public async Task<long> CreateZipAsync(
        string sourceFolderPath,
        string destinationZipPath,
        IProgress<string>? progress,
        CancellationToken ct)
    {
        var files = Directory
            .EnumerateFiles(sourceFolderPath, "*", SearchOption.AllDirectories)
            .ToList();

        _logger.LogInformation("Zipping {Count} files from {Source} → {Dest}", files.Count, sourceFolderPath, destinationZipPath);

        await using var zipStream = new FileStream(destinationZipPath, FileMode.Create, FileAccess.Write, FileShare.None, CopyBufferSize, useAsync: true);
        using var archive = new ZipArchive(zipStream, ZipArchiveMode.Create, leaveOpen: false);

        foreach (var filePath in files)
        {
            ct.ThrowIfCancellationRequested();

            var entryName = Path.GetRelativePath(sourceFolderPath, filePath);
            var entry = archive.CreateEntry(entryName, CompressionLevel.Optimal);

            await using var entryStream = entry.Open();
            await using var fileStream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read, CopyBufferSize, useAsync: true);
            await fileStream.CopyToAsync(entryStream, CopyBufferSize, ct);

            progress?.Report(entryName);
        }

        return new FileInfo(destinationZipPath).Length;
    }
}
