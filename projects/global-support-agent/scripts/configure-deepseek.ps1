[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$secureKey = Read-Host "Enter DeepSeek API Key (input is hidden)" -AsSecureString
$keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)

try {
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    if ([string]::IsNullOrWhiteSpace($plainKey) -or -not $plainKey.StartsWith("sk-")) {
        throw "Invalid API Key: a DeepSeek API Key must start with sk-."
    }

    $settings = @{
        MODEL_PROVIDER = "openai_compatible"
        MODEL_BASE_URL = "https://api.deepseek.com"
        MODEL_NAME = "deepseek-v4-flash"
        MODEL_TIMEOUT_SECONDS = "15"
        MODEL_API_KEY = $plainKey
    }

    foreach ($item in $settings.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable(
            $item.Key,
            $item.Value,
            [EnvironmentVariableTarget]::User
        )
        Set-Item -Path "Env:$($item.Key)" -Value $item.Value
    }

    Write-Host ""
    Write-Host "DeepSeek settings were saved to Windows user environment variables." -ForegroundColor Green
    Write-Host "Model: deepseek-v4-flash"
    Write-Host "Base URL: https://api.deepseek.com"
    Write-Host "API Key: configured (hidden)"
    Write-Host ""
    Write-Host "Restart the diagnostic service to apply the new settings."
}
finally {
    if ($keyPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
    }
    $plainKey = $null
    $secureKey = $null
}
