using System.ComponentModel.DataAnnotations;

namespace FileArchiver.Worker.Configuration;

public sealed class CrmConfig : ICrmConfig
{
    public const string SectionName = "Crm";

    [Required]
    public string ServiceUrl { get; init; } = string.Empty;

    public bool IsIfd { get; init; } = false;

    // ADFS
    public string AdfsUrl { get; init; } = string.Empty;
    public string ClientExternal { get; init; } = string.Empty;
    public string ClientInternal { get; init; } = string.Empty;

    // AD / NetworkCredential
    public string Domain { get; init; } = string.Empty;

    // Credentials (store encrypted; extend Decrypt() in CrmExtensions if needed)
    public string Name { get; init; } = string.Empty;
    public string Code { get; init; } = string.Empty;
}
