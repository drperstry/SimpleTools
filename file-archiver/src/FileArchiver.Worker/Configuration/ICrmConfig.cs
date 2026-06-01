using System.ComponentModel.DataAnnotations;

namespace FileArchiver.Worker.Configuration;

/// <summary>
/// CRM connection configuration — mirrors BabCrm.Crm.Configuration.ICrmConfig.
/// </summary>
public interface ICrmConfig
{
    /// <summary>Web API base URL, e.g. https://org.crm.dynamics.com/api/data/v9.2/</summary>
    string ServiceUrl { get; }

    /// <summary>When true, authenticates via ADFS password grant; otherwise uses NetworkCredential (AD).</summary>
    bool IsIfd { get; }

    // --- ADFS / OAuth ---
    string AdfsUrl { get; }
    string ClientExternal { get; }   // client_id
    string ClientInternal { get; }   // client_secret

    // --- AD / NetworkCredential ---
    string Domain { get; }

    // --- Shared (username / password, may be encrypted) ---
    string Name { get; }
    string Code { get; }
}
