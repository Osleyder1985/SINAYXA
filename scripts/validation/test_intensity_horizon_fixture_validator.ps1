[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$validatorPath = Join-Path $PSScriptRoot "validate_intensity_horizon_fixture.ps1"
$fixturePath = Join-Path $PSScriptRoot "..\..\tests\fixtures\methodology\intensity-horizons\t01-t19-synthetic-evidence-v1.2.0.json"
$fixturePath = (Resolve-Path -LiteralPath $fixturePath).Path
$tempDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-ih-validator-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDirectory | Out-Null

function Get-TestFixture {
    param([string]$Path)
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json -DateKind String)
}

function Invoke-ExpectedFailure {
    param(
        [string]$Name,
        [scriptblock]$Mutation,
        [string]$ExpectedMessage
    )

    $fixture = Get-TestFixture -Path $fixturePath
    & $Mutation $fixture
    $mutatedPath = Join-Path $tempDirectory ($Name + ".json")
    $fixture | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $mutatedPath -Encoding UTF8

    $failedAsExpected = $false
    try {
        & $validatorPath -FixturePath $mutatedPath | Out-Null
    }
    catch {
        if ($_.Exception.Message -like "*$ExpectedMessage*") {
            $failedAsExpected = $true
        }
        else {
            throw "$Name failed for an unexpected reason: $($_.Exception.Message)"
        }
    }

    if (-not $failedAsExpected) {
        throw "$Name was not rejected with the expected validation message: $ExpectedMessage"
    }
    Write-Information ("Negative test " + $Name + ": PASS") -InformationAction Continue
}

try {
    # Positive control: the validator's default path must select v1.2.0.
    $validatorSource = Get-Content -LiteralPath $validatorPath -Raw -Encoding UTF8
    if ($validatorSource -notlike '*t01-t19-synthetic-evidence-v1.2.0.json*') {
        throw "Validator default path does not target the v1.2.0 fixture."
    }
    & $validatorPath
    Write-Information "Positive default-fixture test: PASS" -InformationAction Continue

    Invoke-ExpectedFailure -Name "reject-wrong-iana-zone" -ExpectedMessage "IANA timezone Europe/Madrid" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T18" }
        $case.evidence[0].timezone = "Europe/Paris"
    }

    Invoke-ExpectedFailure -Name "reject-madrid-offset-mismatch" -ExpectedMessage "offset consistency" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T18" }
        $case.evidence[0].start = "2026-03-28T12:00:00+02:00"
    }

    Invoke-ExpectedFailure -Name "reject-timestamp-without-offset" -ExpectedMessage "explicit UTC designator or numeric offset" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T11" }
        $case.evidence[0].reference = "2026-01-01T00:00:00"
    }

    Invoke-ExpectedFailure -Name "reject-wrong-t19-categories" -ExpectedMessage "T19 compatible_categories mismatch" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T19" }
        $case.expected.compatible_categories = @("CORTO", "MEDIO")
    }

    Invoke-ExpectedFailure -Name "reject-wrong-t15-categories" -ExpectedMessage "T15 compatible_categories mismatch" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T15" }
        $case.expected.compatible_categories = @("INMEDIATO")
    }

    Invoke-ExpectedFailure -Name "reject-wrong-t14-milestone" -ExpectedMessage "exactly announcement, approval, effective, and implementation" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T14" }
        $case.evidence[0].milestones[2].name = "activation"
    }

    Invoke-ExpectedFailure -Name "reject-broken-t01-semantic-contract" -ExpectedMessage "T01 v1.2.0" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T01" }
        $case.expected.intensity = "I1"
    }

    Invoke-ExpectedFailure -Name "reject-invalid-date-only" -ExpectedMessage "valid calendar date" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T13" }
        $case.evidence[0].date_only = "2026-02-30"
    }

    Invoke-ExpectedFailure -Name "reject-duplicate-case-id" -ExpectedMessage "Duplicate case IDs" -Mutation {
        param($Fixture)
        $Fixture.cases[1].id = $Fixture.cases[0].id
    }

    Invoke-ExpectedFailure -Name "reject-wrong-t18-elapsed-seconds" -ExpectedMessage "T18 Europe/Madrid offset consistency" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T18" }
        $case.evidence[0].expected_elapsed_seconds = 82800
    }


    Invoke-ExpectedFailure -Name "reject-missing-required-field" -ExpectedMessage "missing a required fixture field" -Mutation {
        param($Fixture)
        $Fixture.cases[0].unit = $null
    }

    Invoke-ExpectedFailure -Name "reject-invalid-timestamp-type" -ExpectedMessage "Timestamp must include an explicit UTC designator or numeric offset" -Mutation {
        param($Fixture)
        $case = $Fixture.cases | Where-Object { $_.id -eq "T11" }
        $case.evidence[0].reference = "not-a-timestamp"
    }

    Write-Information "Negative validator tests: PASS (12 mutation cases)" -InformationAction Continue
}
finally {
    if (Test-Path -LiteralPath $tempDirectory) {
        Remove-Item -LiteralPath $tempDirectory -Recurse -Force
    }
}
