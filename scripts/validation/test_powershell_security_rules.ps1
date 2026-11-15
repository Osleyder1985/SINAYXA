[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Import-Module PSScriptAnalyzer -RequiredVersion 1.24.0

$tempDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-security-rules-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDirectory | Out-Null

$cases = @(
    [pscustomobject]@{
        Name = "plaintext-password-parameter"
        Rule = "PSAvoidUsingPlainTextForPassword"
        Source = "function Test-SecretInput {`n    [CmdletBinding()]`n    param([string]`$Password)`n}"
    }
    [pscustomobject]@{
        Name = "dynamic-expression-execution"
        Rule = "PSAvoidUsingInvokeExpression"
        Source = "Invoke-Expression 'Get-Process'"
    }
    [pscustomobject]@{
        Name = "plaintext-secure-string-conversion"
        Rule = "PSAvoidUsingConvertToSecureStringWithPlainText"
        Source = "ConvertTo-SecureString 'not-a-secret' -AsPlainText -Force"
    }
    [pscustomobject]@{
        Name = "hardcoded-computer-name"
        Rule = "PSAvoidUsingComputerNameHardcoded"
        Source = "Invoke-Command -ComputerName 'server.example.invalid' -ScriptBlock { Get-Process }"
    }
)

try {
    foreach ($case in $cases) {
        $scriptPath = Join-Path $tempDirectory ($case.Name + ".ps1")
        Set-Content -LiteralPath $scriptPath -Value $case.Source -Encoding utf8
        $findings = @(Invoke-ScriptAnalyzer -Path $scriptPath)
        $matchedFinding = @($findings | Where-Object { $_.RuleName -eq $case.Rule })
        if ($matchedFinding.Count -eq 0) {
            throw "Security regression test '$($case.Name)' did not trigger expected rule '$($case.Rule)'."
        }
        Write-Information ("Security regression test {0} ({1}): PASS" -f $case.Name, $case.Rule) -InformationAction Continue
    }
    Write-Information "Security regression tests: PASS (4 rules)" -InformationAction Continue
}
finally {
    if (Test-Path -LiteralPath $tempDirectory) {
        Remove-Item -LiteralPath $tempDirectory -Recurse -Force
    }
}

if (Test-Path -LiteralPath $tempDirectory) {
    throw "Security test temporary directory was not cleaned up."
}
Write-Information "Security test cleanup: PASS" -InformationAction Continue
