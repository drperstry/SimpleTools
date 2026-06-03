using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Services;
using FileArchiver.Worker.Workers;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

bool runNow = args.Contains("--run-now");

var host = Host.CreateDefaultBuilder(args)
    .ConfigureAppConfiguration(config =>
    {
        if (runNow)
            config.AddInMemoryCollection(new Dictionary<string, string?> { ["RunNow"] = "true" });
    })
    .UseSerilog((ctx, lc) => lc.ReadFrom.Configuration(ctx.Configuration))
    .ConfigureServices((ctx, services) =>
    {
        services.AddOptions<ArchivalOptions>()
            .BindConfiguration(ArchivalOptions.SectionName)
            .ValidateDataAnnotations()
            .ValidateOnStart();

        services.AddOptions<CrmConfig>()
            .BindConfiguration(CrmConfig.SectionName)
            .ValidateDataAnnotations()
            .ValidateOnStart();

        services.AddSingleton<ICrmConfig>(sp =>
            sp.GetRequiredService<Microsoft.Extensions.Options.IOptions<CrmConfig>>().Value);

        var dryRun = ctx.Configuration.GetSection(ArchivalOptions.SectionName)
            .GetValue<bool>("DryRun");

        if (dryRun)
        {
            Log.Information("DryRun=true — using fake CRM and Zip services");
            services.AddSingleton<ICrmService, FakeCrmService>();
            services.AddSingleton<IZipService, FakeZipService>();
        }
        else
        {
            services.AddSingleton<ICrmService, CrmService>();
            services.AddSingleton<IZipService, ZipService>();
        }

        services.AddTransient<IFileArchivalService, FileArchivalService>();
        services.AddHostedService<ArchivalWorker>();
    })
    .Build();

await host.RunAsync();
