from pathlib import Path


RUNNER = Path(__file__).parents[2] / "test_m8.ps1"


def test_frontend_compose_progress_is_captured_without_native_pipeline() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    section = text.split('$frontendCommand =', 1)[1].split('$dockerCommand =', 1)[0]
    assert 'Invoke-NativeCapture -FilePath "cmd.exe"' in section
    assert 'cmd.exe /d /s /c $frontendCommand 2>&1' not in section
    assert '$frontendResult.ExitCode' in section
