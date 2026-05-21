"""Upload dbt artifacts from target/ to GCS in a hive-partitioned layout.

Raw JSON artifacts are uploaded as-is. run_results.json is also flattened to
run_results.parquet so BigQuery can expose it via an external table.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import storage

RAW_ARTIFACTS = ["manifest.json", "run_results.json", "catalog.json", "sources.json"]


def flatten_run_results(target: Path) -> Path | None:
    src = target / "run_results.json"
    if not src.exists():
        return None
    data = json.loads(src.read_text())
    metadata = data.get("metadata") or {}
    invocation_id = metadata.get("invocation_id")
    generated_at = metadata.get("generated_at")
    elapsed_time = data.get("elapsed_time")

    rows = []
    for r in data.get("results") or []:
        rows.append({
            "invocation_id": invocation_id,
            "generated_at": generated_at,
            "elapsed_time": elapsed_time,
            "unique_id": r.get("unique_id"),
            "status": r.get("status"),
            "execution_time": r.get("execution_time"),
            "message": r.get("message"),
            "raw": r,
        })

    out = target / "run_results.parquet"
    pq.write_table(pa.Table.from_pylist(rows), out)
    return out


def main() -> int:
    bucket_name = os.environ["ARTIFACTS_BUCKET"]
    project = os.environ.get("DBT_PROJECT_NAME", "po_data_demos")
    run_id = os.environ.get("CLOUD_RUN_EXECUTION") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    prefix = f"dbt-artifacts/project={project}/dt={dt}/run_id={run_id}"
    bucket = storage.Client().bucket(bucket_name)
    target = Path("target")

    files_to_upload = [target / name for name in RAW_ARTIFACTS if (target / name).exists()]
    parquet = flatten_run_results(target)
    if parquet is not None:
        files_to_upload.append(parquet)

    for path in files_to_upload:
        bucket.blob(f"{prefix}/{path.name}").upload_from_filename(str(path))

    names = [p.name for p in files_to_upload]
    print(f"uploaded {len(names)} artifact(s) to gs://{bucket_name}/{prefix}/: {names}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"artifact upload failed: {e}", file=sys.stderr)
        sys.exit(0)
