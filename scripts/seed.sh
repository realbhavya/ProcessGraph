#!/usr/bin/env sh
set -eu
set -a
[ -f .env ] && . ./.env
set +a
python graph/seed/seed.py --reset
python graph/validate.py
