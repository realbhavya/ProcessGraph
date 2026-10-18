$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path "test-results" | Out-Null
$LogFile = Join-Path $PSScriptRoot "test-results\milestone-6-latest.log"
$TestGraph = "processgraph_test_$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())_$PID"
$OriginalRunning = @()
$ExitCode = 1

function Write-Step([string]$Message) {
    Write-Host $Message -ForegroundColor Cyan
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$ArgumentList
    )
    $stdout = [System.IO.Path]::GetTempFileName()
    $stderr = [System.IO.Path]::GetTempFileName()
    try {
        $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        return [PSCustomObject]@{
            ExitCode = $process.ExitCode
            StdOut = (Get-Content $stdout -Raw -ErrorAction SilentlyContinue)
            StdErr = (Get-Content $stderr -Raw -ErrorAction SilentlyContinue)
        }
    }
    finally {
        Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue
    }
}

function Get-RunningServices {
    $result = Invoke-NativeCapture -FilePath "docker" -ArgumentList @("compose", "ps", "--services", "--status", "running")
    if ($result.ExitCode -ne 0) { return @() }
    return @($result.StdOut -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^[A-Za-z0-9][A-Za-z0-9_.-]*$' })
}

try {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " ProcessGraph Sentinel - Milestone 6 Verification" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Step "[START] Initializing native Windows test runner..."

    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker command not found. Install and start Docker Desktop."
    }

    $composeCheck = Invoke-NativeCapture -FilePath "docker" -ArgumentList @("compose", "version")
    if ($composeCheck.StdOut) { Write-Host $composeCheck.StdOut.Trim() }
    if ($composeCheck.ExitCode -ne 0) { throw "Docker Compose is unavailable. $($composeCheck.StdErr)" }

    Write-Step "[CHECK] Verifying Docker Desktop engine..."
    $dockerCheck = Invoke-NativeCapture -FilePath "docker" -ArgumentList @("info", "--format", "{{.ServerVersion}}")
    if ($dockerCheck.ExitCode -ne 0) {
        throw "Docker Desktop engine is not running. $($dockerCheck.StdErr)"
    }
    Write-Host "[CHECK] Docker engine available: $($dockerCheck.StdOut.Trim())" -ForegroundColor Green
    if ($dockerCheck.StdErr) {
        Write-Host "[INFO] Docker reported non-fatal capability warnings; continuing." -ForegroundColor DarkYellow
    }

    if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
    $OriginalRunning = @(Get-RunningServices)
    Write-Step "[SETUP] Services running before test: $(if ($OriginalRunning.Count) { $OriginalRunning -join ', ' } else { 'none' })"

    # Set the isolated graph before Compose resolves the override file and before
    # the backend container is created. This guarantees that both the backend and
    # test runner target the same temporary graph, never the application graph.
    $env:FALKORDB_TEST_GRAPH = $TestGraph
    Write-Step "[SETUP] Isolated graph: $TestGraph"
    Write-Step "[SETUP] Starting FalkorDB and API..."
    & docker compose -f docker-compose.yml -f docker-compose.m6-test.yml up -d falkordb backend
    if ($LASTEXITCODE -ne 0) { throw "Unable to start FalkorDB." }

    Write-Step "[TEST] Running all checks inside an isolated Docker test container..."

    # Docker Compose writes normal progress messages such as "Container ... Running"
    # to stderr. PowerShell can promote those messages to ErrorRecord objects when
    # native output is piped, so execute Docker through cmd.exe and use its real exit code.
    $dockerCommand = "docker compose -f docker-compose.yml -f docker-compose.m6-test.yml --profile test run --rm --build test-runner"
    $testResult = Invoke-NativeCapture -FilePath "cmd.exe" -ArgumentList @("/d", "/s", "/c", $dockerCommand)

    $combinedOutput = @()
    if ($testResult.StdOut) { $combinedOutput += $testResult.StdOut.TrimEnd() }
    if ($testResult.StdErr) { $combinedOutput += $testResult.StdErr.TrimEnd() }
    $combinedText = $combinedOutput -join [Environment]::NewLine
    if ($combinedText) {
        $combinedText | Tee-Object -FilePath $LogFile | Write-Host
    }

    $ExitCode = $testResult.ExitCode
    if ($ExitCode -ne 0) {
        throw "Test container failed with exit code $ExitCode. Review $LogFile for the complete output."
    }

    Write-Host "[RESULT] ALL TESTS PASSED" -ForegroundColor Green
    $ExitCode = 0
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    if ($ExitCode -eq 0) { $ExitCode = 1 }
}
finally {
    Write-Step "[RESTORE] Restoring service state..."
    $NowRunning = @(Get-RunningServices)
    foreach ($Service in $NowRunning) {
        if ([string]::IsNullOrWhiteSpace($Service)) { continue }
        if ($OriginalRunning -notcontains $Service) {
            Write-Step "[RESTORE] Stopping service started by test: $Service"
            $stop = Invoke-NativeCapture -FilePath "docker" -ArgumentList @("compose", "stop", $Service)
            if ($stop.ExitCode -ne 0) {
                Write-Host "[WARN] Could not stop $Service automatically." -ForegroundColor Yellow
            }
        }
    }
    Remove-Item Env:FALKORDB_TEST_GRAPH -ErrorAction SilentlyContinue
    if ($ExitCode -eq 0) {
        Write-Host "[RESTORE] Project state restored successfully" -ForegroundColor Green
    } else {
        Write-Host "[RESTORE] Project state restored after test failure" -ForegroundColor Yellow
    }
    Write-Host "[LOG] $LogFile"
}
exit $ExitCode
