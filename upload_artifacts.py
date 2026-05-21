"""Upload dbt artifacts from target/ to GCS in a hive-partitioned layout."""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import storage

ARTIFACTS = ["manifest.json", "run_results.json", "catalog.json", "sources.json"]


def main() -> int:
    bucket_name = os.environ["ARTIFACTS_BUCKET"]
    project = os.environ.get("DBT_PROJECT_NAME", "po_data_demos")
    run_id = os.environ.get("CLOUD_RUN_EXECUTION") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    prefix = f"dbt-artifacts/project={project}/dt={dt}/run_id={run_id}"
    bucket = storage.Client().bucket(bucket_name)
    target = Path("target")

    uploaded = []
    for name in ARTIFACTS:
        path = target / name
        if not path.exists():
            continue
        bucket.blob(f"{prefix}/{name}").upload_from_filename(str(path))
        uploaded.append(name)

    print(f"uploaded {len(uploaded)} artifact(s) to gs://{bucket_name}/{prefix}/: {uploaded}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"artifact upload failed: {e}", file=sys.stderr)
        sys.exit(0)
