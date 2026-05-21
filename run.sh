#!/bin/sh
set -u

echo "=== dbt build ==="
dbt build
rc=$?

echo "=== upload artifacts ==="
python upload_artifacts.py

exit $rc
