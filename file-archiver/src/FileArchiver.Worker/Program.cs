using FileArchiver.Worker.Configuration;
using FileArchiver.Worker.Services;
using FileArchiver.Worker.Workers;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.PowerPlatform.Dataverse.Client;
using Serilog;

bool runNow = args.Contains("--run-now");

var host = Host.CreateDefaultBuilder(args)
    .UseSerilog((ctx, lc) => lc.ReadFrom.Configuration(ctx.Configuration))
    .ConfigureServices((ctx, services) =>
    {
        services.AddOptions<ArchivalOptions>()
            .BindConfiguration(ArchivalOptions.SectionName)
            .ValidateDataAnnotations()
            .ValidateOnStart();

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
            services.AddSingleton<ServiceClient>(sp =>
            {
                var connStr = ctx.Configuration["Dataverse:ConnectionString"]
                    ?? throw new InvalidOperationException("Dataverse:ConnectionString is required when DryRun=false");
                return new ServiceClient(connStr);
            });

            services.AddSingleton<ICrmService, CrmService>();
            services.AddSingleton<IZipService, ZipService>();
        }

        services.AddTransient<IFileArchivalService, FileArchivalService>();
        services.AddSingleton(runNow);
        services.AddHostedService<ArchivalWorker>();
    })
    .Build();

await host.RunAsync();
