namespace FileArchiver.Worker.Services;

public interface IZipService
{
    Task<long> CreateZipAsync(
        string sourceFolderPath,
        string destinationZipPath,
        IProgress<string>? progress,
        CancellationToken ct);
}
