from pathlib import Path


def test_pytest_uses_importlib_mode_for_test_module_isolation() -> None:
    config = (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    assert '--import-mode=importlib' in config
