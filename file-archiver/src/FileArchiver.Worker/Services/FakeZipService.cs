using Microsoft.Extensions.Logging;

namespace FileArchiver.Worker.Services;

public sealed class FakeZipService : IZipService
{
    private readonly ILogger<FakeZipService> _logger;

    public FakeZipService(ILogger<FakeZipService> logger) => _logger = logger;

    public async Task<long> CreateZipAsync(
        string sourceFolderPath,
        string destinationZipPath,
        IProgress<string>? progress,
        CancellationToken ct)
    {
        // Actually create the zip so dry-run exercises the real file path logic
        var zipService = new ZipService(_logger as ILogger<ZipService>
            ?? Microsoft.Extensions.Logging.Abstractions.NullLogger<ZipService>.Instance);

        var size = await zipService.CreateZipAsync(sourceFolderPath, destinationZipPath, progress, ct);
        _logger.LogInformation("[DryRun] Created zip: {Path} ({Bytes:N0} bytes)", destinationZipPath, size);
        return size;
    }
}
