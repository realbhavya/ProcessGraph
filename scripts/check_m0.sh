#!/usr/bin/env sh
set -eu
printf '%s\n' '[M0] Checking required files'
test -f README.md
test -f .env.example
test -f docker-compose.yml
test -f docs/product-requirements.md
test -f docs/architecture-overview.md
test -f docs/safety-boundaries.md
printf '%s\n' '[M0] Running backend foundation tests'
python -m pytest -q backend/tests/test_health.py
printf '%s\n' '[M0] Milestone 0 checks passed'
