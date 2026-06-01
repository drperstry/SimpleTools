using FileArchiver.Worker.Services;

namespace FileArchiver.Tests.Fakes;

public sealed class FakeZipService : IZipService
{
    public long ReturnSize { get; set; } = 1024;
    public int CallCount { get; private set; }
    public int ThrowCount { get; set; } = 0;

    private int _calls = 0;

    public Task<long> CreateZipAsync(string sourceFolderPath, string destinationZipPath, IProgress<string>? progress, CancellationToken ct)
    {
        CallCount++;
        _calls++;

        if (_calls <= ThrowCount)
            throw new IOException($"Simulated zip failure #{_calls}");

        return Task.FromResult(ReturnSize);
    }
}
