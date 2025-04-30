# Get all the files in the current directory
$files = Get-ChildItem -File
$results = @()

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName

    $uptime = $content | Where-Object { $_ -match 'uptime' } | Select-Object -First 1
    $hostname = if ($uptime) { ($uptime -split '\s+')[0] } else { "" }

    $image = $content | Where-Object { $_ -match 'image file is' } | Select-Object -First 1

    $cpuUtil = $content | Where-Object { $_ -match 'cpu util' } | Select-Object -First 1

    $systemSerialNumbers = $content | Where-Object { $_ -match 'System Serial Number' }

    $processorBoardIDIndex = $null
    for ($i = 0; $i -lt $content.Count; $i++) {
        if ($content[$i] -match 'Processor board ID') {
            $processorBoardIDIndex = $i
            break
        }
    }

    $blockLines = @()
    if ($processorBoardIDIndex -ne $null) {
        $startIndex = $processorBoardIDIndex
        for ($j = $processorBoardIDIndex - 1; $j -ge 0; $j--) {
            if ($content[$j] -eq "") { break }
            $startIndex = $j
        }

        for ($k = $startIndex; $k -lt $content.Count; $k++) {
            if ($content[$k] -eq "") { break }
            $blockLines += $content[$k]
        }
    }

    # Extract Inventory Section
    $inventoryIndex = $null
    for ($i = 0; $i -lt $content.Count; $i++) {
        if ($content[$i] -match 'inventory') {
            $inventoryIndex = $i
            break
        }
    }

    $inventoryCapture = @()
    if ($inventoryIndex -ne $null) {
        $emptyLineCount = 0
        for ($i = $inventoryIndex + 1; $i -lt $content.Count; $i++) {
            $line = $content[$i]
            if ($line -eq "") {
                $emptyLineCount++
                if ($emptyLineCount -ge 2) { break }
            } else {
                $emptyLineCount = 0
            }
            $inventoryCapture += $line
        }
    }

    # Extract Model from line after "PID:"
    $model = ""
    if ($inventoryCapture.Count -ge 2) {
        $modelLine = $inventoryCapture[1]
        if ($modelLine -match 'PID:\s*(\S+)') {
            $model = $matches[1]
        }
    }


    $version = ""
    for ($i = 0; $i -lt $content.Count; $i++) {
        if ($content[$i] -match 'show version') {
            if ($i + 1 -lt $content.Count) {
                $nextLine = $content[$i + 1]
                if ($nextLine -match 'Version\s+([^\s,;]+)') {
                    $version = $matches[1]
                }
            }
            break
        }
    }

    # Initialize status variables
    $statusLines = @()

    # Search for lines with both "(D)" and "(P)" on the same line
    foreach ($line in $content) {
        if ($line -match '\(D\)' -and $line -match '\(P\)') {
            $statusLines += $line
        }
    }

    # Search for "bad" and "pwr" with an empty line between
    $badLine = $null
    $pwrLine = $null
    $emptyLineCount = 0

    for ($i = 0; $i -lt $content.Count; $i++) {
        if ($content[$i] -match 'bad') {
            $badLine = $content[$i]
            $emptyLineCount = 0
        }

        if ($badLine -ne $null -and $content[$i] -match 'pwr') {
            $pwrLine = $content[$i]
            break
        }
        
        # Count empty lines between "bad" and "pwr"
        if ($badLine -ne $null -and $content[$i] -eq "") {
            $emptyLineCount++
            if ($emptyLineCount -gt 1) {
                $badLine = $null  # Reset if there are too many empty lines
            }
        }
    }

    # Prepare the Status Section
    $statusSection = ""

    # Include the (D) and (P) lines
    if ($statusLines.Count -gt 0) {
        $statusSection += ($statusLines -join "`n") + "`n"
    }

    # Include the Bad and Pwr lines if found
    if ($badLine -ne $null -and $pwrLine -ne $null) {
        $statusSection += "`n$badLine`n$pwrLine"
    }

    # Create custom object
    $results += [PSCustomObject]@{
        SN = ""
        Type = ""
        Model                  = $model
        Hostname               = $hostname
        IPAddress              = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        ios_Version = $version
        Suggeted_ios_version = ""
        Image                  = $image
        SystemSerialNumbers    = ($systemSerialNumbers -join "`n")
        Uptime                 = $uptime
        CPUUtilization         = $cpuUtil
        InventorySection       = ($inventoryCapture -join "`n")
        ProcessorBoardSection  = ($blockLines -join "`n")
        Status                 = $statusSection
    }
}

# Export to CSV
$results | Export-Csv -Path ".\output.csv" -NoTypeInformation -Encoding UTF8

Write-Host "Exported results to output.csv"
