using System.IO.Compression;
using FileArchiver.Worker.Services;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace FileArchiver.Tests.Services;

public sealed class ZipServiceTests : IDisposable
{
    private readonly string _tempRoot = Path.Combine(Path.GetTempPath(), $"ZipTest_{Guid.NewGuid()}");

    public ZipServiceTests() => Directory.CreateDirectory(_tempRoot);

    public void Dispose() => Directory.Delete(_tempRoot, recursive: true);

    [Fact]
    public async Task CreateZipAsync_CreatesZipWithAllFiles()
    {
        var sourceDir = Path.Combine(_tempRoot, "source");
        Directory.CreateDirectory(sourceDir);
        await File.WriteAllTextAsync(Path.Combine(sourceDir, "a.txt"), "hello");
        await File.WriteAllTextAsync(Path.Combine(sourceDir, "b.txt"), "world");
        await File.WriteAllTextAsync(Path.Combine(sourceDir, "c.txt"), "!");

        var zipPath = Path.Combine(_tempRoot, "out.zip");
        var svc = new ZipService(NullLogger<ZipService>.Instance);

        var size = await svc.CreateZipAsync(sourceDir, zipPath, null, CancellationToken.None);

        Assert.True(File.Exists(zipPath));
        Assert.Equal(new FileInfo(zipPath).Length, size);

        using var archive = ZipFile.OpenRead(zipPath);
        Assert.Equal(3, archive.Entries.Count);
        var names = archive.Entries.Select(e => e.Name).OrderBy(n => n).ToList();
        Assert.Equal(new[] { "a.txt", "b.txt", "c.txt" }, names);
    }

    [Fact]
    public async Task CreateZipAsync_ReportsProgressForEachFile()
    {
        var sourceDir = Path.Combine(_tempRoot, "progress_source");
        Directory.CreateDirectory(sourceDir);
        await File.WriteAllTextAsync(Path.Combine(sourceDir, "x.txt"), "data");
        await File.WriteAllTextAsync(Path.Combine(sourceDir, "y.txt"), "data");

        var reported = new List<string>();
        var progress = new Progress<string>(s => reported.Add(s));
        var svc = new ZipService(NullLogger<ZipService>.Instance);

        await svc.CreateZipAsync(sourceDir, Path.Combine(_tempRoot, "p.zip"), progress, CancellationToken.None);

        await Task.Delay(50); // allow progress callbacks to fire
        Assert.Equal(2, reported.Count);
    }

    [Fact]
    public async Task CreateZipAsync_PreservesSubdirectoryStructure()
    {
        var sourceDir = Path.Combine(_tempRoot, "nested_source");
        var subDir = Path.Combine(sourceDir, "sub");
        Directory.CreateDirectory(subDir);
        await File.WriteAllTextAsync(Path.Combine(sourceDir, "root.txt"), "r");
        await File.WriteAllTextAsync(Path.Combine(subDir, "nested.txt"), "n");

        var zipPath = Path.Combine(_tempRoot, "nested.zip");
        var svc = new ZipService(NullLogger<ZipService>.Instance);

        await svc.CreateZipAsync(sourceDir, zipPath, null, CancellationToken.None);

        using var archive = ZipFile.OpenRead(zipPath);
        var names = archive.Entries.Select(e => e.FullName).OrderBy(n => n).ToList();
        Assert.Contains("root.txt", names);
        Assert.Contains(names, n => n.Contains("nested.txt"));
    }
}
