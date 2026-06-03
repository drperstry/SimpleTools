using Newtonsoft.Json.Linq;
using System.Net.Http.Headers;

namespace FileArchiver.Worker.Configuration;

/// <summary>
/// Mirrors BabCrm.Crm.Extensions — builds an authenticated HttpClient from ICrmConfig.
/// </summary>
internal static class CrmExtensions
{
    internal static HttpClient BuildClient(this ICrmConfig crmConfig)
        => crmConfig.IsIfd ? BuildClientAdfs(crmConfig) : BuildClientAd(crmConfig);

    private static HttpClient BuildClientAdfs(ICrmConfig crmConfig)
    {
        using var tokenClient = new HttpClient();
        var returnClient = new HttpClient();

        var dict = new Dictionary<string, string>
        {
            ["client_id"]     = crmConfig.ClientExternal,
            ["client_secret"] = crmConfig.ClientInternal,
            ["resource"]      = crmConfig.ServiceUrl,
            ["username"]      = crmConfig.Name,
            ["password"]      = crmConfig.Code,
            ["grant_type"]    = "password"
        };

        var req = new HttpRequestMessage(HttpMethod.Post, crmConfig.AdfsUrl)
        {
            Content = new FormUrlEncodedContent(dict)
        };

        var res = tokenClient.SendAsync(req).GetAwaiter().GetResult();

        if (res.IsSuccessStatusCode)
        {
            var body = JObject.Parse(res.Content.ReadAsStringAsync().GetAwaiter().GetResult());
            var accessToken = (string?)body["access_token"];
            if (!string.IsNullOrEmpty(accessToken))
                returnClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", accessToken);
        }

        returnClient.BaseAddress = new Uri(crmConfig.ServiceUrl);
        return returnClient;
    }

    private static HttpClient BuildClientAd(ICrmConfig crmConfig)
    {
        var handler = new HttpClientHandler
        {
            UseDefaultCredentials = true,
            PreAuthenticate = true
        };

        return new HttpClient(handler) { BaseAddress = new Uri(crmConfig.ServiceUrl) };
    }
}
