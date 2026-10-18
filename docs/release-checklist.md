# Release Checklist

- Run `test_m10.bat` from a clean extraction.
- Require the full regression and 22-case deterministic evaluation harness to pass.
- Require production smoke, capability assertions, metrics, and final graph validation.
- Verify clean restoration.
- Review dependency changes and container tags.
- Confirm no secrets, generated test results, caches, or runtime graph exports are bundled.
- Confirm the UI states synthetic-only and no plant control is available.
