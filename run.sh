#!/bin/sh
# Exit immediately if any command in this script throws an error
set -e  

echo "=== Running Staging Models and Data Quality Tests ==="
dbt build