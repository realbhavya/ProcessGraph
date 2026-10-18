#!/usr/bin/env sh
set -eu
python -m pytest -q backend
python graph/validate.py
printf '%s\n' '[M1] Milestone 1 checks passed'
