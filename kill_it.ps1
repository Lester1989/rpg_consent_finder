Get-Process -Name python | ForEach-Object {
    $process = $_
    $processInfo = Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)"
    [PSCustomObject]@{
        Name     = $process.Name
        Id       = $process.Id
        FilePath = $processInfo.ExecutablePath
    }
} | Where-Object { $_.FilePath -like '*consent*' } | ForEach-Object {
    Stop-Process -Id $_.Id -Force
    Write-Output "Killed process $($_.Name) with Id $($_.Id) at $($_.FilePath)"
}