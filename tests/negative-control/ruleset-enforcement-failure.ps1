# Disposable negative-control fixture. Never merge.
function Invoke-NegativeControl {
    if ($true) {
        Write-Output 'This block is intentionally not closed'
}
