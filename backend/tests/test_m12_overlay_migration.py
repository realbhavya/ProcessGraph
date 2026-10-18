from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_windows_runner_removes_exact_obsolete_overlay_files_before_build() -> None:
    text = (ROOT / "test_m12.ps1").read_text(encoding="utf-8")
    migration = text.split('[MIGRATE] Removing obsolete', 1)[1].split('[TEST] Running all checks', 1)[0]
    assert 'backend\\tests\\opcua\\test_contracts.py' in migration
    assert 'backend\\tests\\test_test_module_names.py' in migration
    assert 'Remove-Item $ObsoleteTestFile -Force' in migration


def test_container_runner_has_defensive_overlay_cleanup() -> None:
    text = (ROOT / "scripts" / "test_m12_container.sh").read_text(encoding="utf-8")
    assert 'rm -f backend/tests/opcua/test_contracts.py backend/tests/test_test_module_names.py' in text
