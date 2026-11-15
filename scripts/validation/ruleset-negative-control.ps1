# INTENTIONAL NEGATIVE CONTROL — DO NOT MERGE.
# This isolated file contains a deliberate parser error to verify protect-main.
function Invoke-RulesetNegativeControl {
    if (
        Write-Output "This syntax is intentionally invalid for the ruleset test."
}
