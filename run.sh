#!/bin/sh
# Exit immediately if any command in this script throws an error
set -e  

echo "=== STEP 1: Refreshing GCS BigLake External Tables ==="
dbt run-operation stage_external_sources

echo "=== STEP 2: Running Staging Models and Data Quality Tests ==="
dbt build