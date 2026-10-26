#!/bin/sh
set -eu
python -m pytest -q
python -m floodlens.experiment
python scripts/render_evaluation.py
python scripts/render_animation.py
(cd frontend && npm run build)
