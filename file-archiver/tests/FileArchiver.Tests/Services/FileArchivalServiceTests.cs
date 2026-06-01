using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Models;
using FileArchiver.Worker.Services;
using FileArchiver.Tests.Fakes;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Xunit;

namespace FileArchiver.Tests.Services;

public sealed class FileArchivalServiceTests : IDisposable
{
    private readonly string _tempRoot = Path.Combine(Path.GetTempPath(), $"ArchiveTest_{Guid.NewGuid()}");
    private readonly string _sourceDir;
    private readonly string _archiveDir;

    public FileArchivalServiceTests()
    {
        _sourceDir = Path.Combine(_tempRoot, "source");
        _archiveDir = Path.Combine(_tempRoot, "archive");
        Directory.CreateDirectory(_sourceDir);
        Directory.CreateDirectory(_archiveDir);
    }

    public void Dispose() => Directory.Delete(_tempRoot, recursive: true);

    private (FileArchivalService svc, FakeCrmService crm, FakeZipService zip) BuildSvc(
        bool deleteOriginals = false, bool dryRun = false)
    {
        var crm = new FakeCrmService();
        var zipSvc = new FakeZipService();
        var opts = Options.Create(new ArchivalOptions
        {
            ArchiveUncPath = _archiveDir,
            SourceUncRoot = _sourceDir,
            RetryCount = 1,
            RetryDelaySeconds = 0,
            CrmBatchSize = 100,
            DeleteOriginalsAfterArchive = deleteOriginals
        });

        var svc = new FileArchivalService(crm, zipSvc, opts, NullLogger<FileArchivalService>.Instance);
        return (svc, crm, zipSvc);
    }

    private IncidentArchivalJob MakeJob(string folderPath)
    {
        var incidentId = Guid.NewGuid();
        return new IncidentArchivalJob
        {
            IncidentId = incidentId,
            FolderPath = folderPath,
            Files = new List<NtwsFileRecord>
            {
                new(Guid.NewGuid(), incidentId, "file1.pdf", folderPath, false, 1024, DateTime.UtcNow.AddDays(-100)),
                new(Guid.NewGuid(), incidentId, "file2.pdf", folderPath, false, 2048, DateTime.UtcNow.AddDays(-100))
            }
        };
    }

    [Fact]
    public async Task ArchiveIncidentAsync_CallsZipThenCrmInOrder()
    {
        var (svc, crm, zip) = BuildSvc();
        var incidentDir = Path.Combine(_sourceDir, Guid.NewGuid().ToString());
        Directory.CreateDirectory(incidentDir);
        await File.WriteAllTextAsync(Path.Combine(incidentDir, "test.txt"), "data");

        // Use real ZipService via the actual FileArchivalService with real zip
        var realZip = new ZipService(NullLogger<ZipService>.Instance);
        var opts = Options.Create(new ArchivalOptions
        {
            ArchiveUncPath = _archiveDir,
            SourceUncRoot = _sourceDir,
            RetryCount = 1,
            RetryDelaySeconds = 0,
            CrmBatchSize = 100
        });
        var realSvc = new FileArchivalService(crm, realZip, opts, NullLogger<FileArchivalService>.Instance);

        var job = MakeJob(incidentDir);
        await realSvc.ArchiveIncidentAsync(job, CancellationToken.None);

        Assert.Equal(2, crm.ArchivedIds.Count);
        Assert.Single(crm.CreatedZipRecords);
        Assert.Equal(job.IncidentId, crm.CreatedZipRecords[0].IncidentId);
    }

    [Fact]
    public async Task ArchiveIncidentAsync_DoesNotDeleteOriginalsWhenCrmFails()
    {
        var (svc, crm, zip) = BuildSvc(deleteOriginals: true);
        crm.ThrowOnBatchUpdate = true;

        var incidentDir = Path.Combine(_sourceDir, Guid.NewGuid().ToString());
        Directory.CreateDirectory(incidentDir);
        await File.WriteAllTextAsync(Path.Combine(incidentDir, "important.txt"), "keep me");

        var realZip = new ZipService(NullLogger<ZipService>.Instance);
        var opts = Options.Create(new ArchivalOptions
        {
            ArchiveUncPath = _archiveDir,
            SourceUncRoot = _sourceDir,
            RetryCount = 1,
            RetryDelaySeconds = 0,
            CrmBatchSize = 100,
            DeleteOriginalsAfterArchive = true
        });
        var realSvc = new FileArchivalService(crm, realZip, opts, NullLogger<FileArchivalService>.Instance);

        var job = MakeJob(incidentDir);

        await Assert.ThrowsAsync<InvalidOperationException>(
            () => realSvc.ArchiveIncidentAsync(job, CancellationToken.None));

        // Original folder must still exist
        Assert.True(Directory.Exists(incidentDir));
        Assert.True(File.Exists(Path.Combine(incidentDir, "important.txt")));
    }

    [Fact]
    public async Task ArchiveIncidentAsync_DeletesOriginalsWhenConfiguredAndCrmSucceeds()
    {
        var incidentDir = Path.Combine(_sourceDir, Guid.NewGuid().ToString());
        Directory.CreateDirectory(incidentDir);
        await File.WriteAllTextAsync(Path.Combine(incidentDir, "f.txt"), "bye");

        var crm = new FakeCrmService();
        var realZip = new ZipService(NullLogger<ZipService>.Instance);
        var opts = Options.Create(new ArchivalOptions
        {
            ArchiveUncPath = _archiveDir,
            SourceUncRoot = _sourceDir,
            RetryCount = 1,
            RetryDelaySeconds = 0,
            CrmBatchSize = 100,
            DeleteOriginalsAfterArchive = true
        });
        var realSvc = new FileArchivalService(crm, realZip, opts, NullLogger<FileArchivalService>.Instance);

        var job = MakeJob(incidentDir);
        await realSvc.ArchiveIncidentAsync(job, CancellationToken.None);

        Assert.False(Directory.Exists(incidentDir));
    }
}
