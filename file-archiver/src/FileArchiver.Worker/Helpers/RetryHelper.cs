using FileArchiver.Worker.Configuration;
using Microsoft.Extensions.Logging;
using Polly;
using Polly.Retry;
using Polly.Timeout;

namespace FileArchiver.Worker.Helpers;

public static class RetryHelper
{
    public static ResiliencePipeline BuildFileRetry(ArchivalOptions opts, ILogger logger) =>
        new ResiliencePipelineBuilder()
            .AddRetry(new RetryStrategyOptions
            {
                MaxRetryAttempts = opts.RetryCount,
                Delay = TimeSpan.FromSeconds(opts.RetryDelaySeconds),
                BackoffType = DelayBackoffType.Exponential,
                ShouldHandle = new PredicateBuilder().Handle<IOException>(),
                OnRetry = args =>
                {
                    logger.LogWarning(
                        "File I/O retry {Attempt}/{Max} after {Delay:N0}ms: {Message}",
                        args.AttemptNumber + 1, opts.RetryCount,
                        args.RetryDelay.TotalMilliseconds,
                        args.Outcome.Exception?.Message);
                    return ValueTask.CompletedTask;
                }
            })
            .AddTimeout(TimeSpan.FromMinutes(30))
            .Build();

    public static ResiliencePipeline BuildCrmRetry(ArchivalOptions opts, ILogger logger) =>
        new ResiliencePipelineBuilder()
            .AddRetry(new RetryStrategyOptions
            {
                MaxRetryAttempts = opts.RetryCount,
                Delay = TimeSpan.FromSeconds(opts.RetryDelaySeconds),
                BackoffType = DelayBackoffType.Exponential,
                ShouldHandle = new PredicateBuilder()
                    .Handle<HttpRequestException>()
                    .Handle<TaskCanceledException>(),
                OnRetry = args =>
                {
                    logger.LogWarning(
                        "CRM retry {Attempt}/{Max} after {Delay:N0}ms: {Message}",
                        args.AttemptNumber + 1, opts.RetryCount,
                        args.RetryDelay.TotalMilliseconds,
                        args.Outcome.Exception?.Message);
                    return ValueTask.CompletedTask;
                }
            })
            .AddTimeout(TimeSpan.FromMinutes(5))
            .Build();
}
