#!/bin/bash
cd python
poetry install
poetry run two-sigma generate-data --samples 100 --output data/train.h5
poetry run two-sigma train --data data/train.h5 --model-path models/model.joblib
poetry run two-sigma evaluate --data data/train.h5 --model-path models/model.joblib
