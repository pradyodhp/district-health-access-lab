"""Rebuild the selected pilot extract from the versioned raw source."""
from pathlib import Path
import sys
import json
import gzip
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from health_access.extract import extract, write_csv  # noqa: E402

if __name__ == "__main__":
    output = ROOT / "data/processed/pilot_indicators.csv"
    manifest = json.loads((ROOT / "data/raw/manifest.json").read_text())
    raw = ROOT / "data/raw" / manifest["file"]
    if raw.name != manifest["file"] or raw.parent != ROOT / "data/raw":
        raise ValueError("Manifest file must be a local raw filename")
    if hashlib.sha256(gzip.open(raw, "rb").read()).hexdigest() != manifest["sha256_uncompressed"]:
        raise ValueError("Raw source checksum mismatch; do not silently repair source data")
    rows = extract(ROOT / "data/raw/nfhs_india_2026-09-30.csv.gz")
    if len(rows) != manifest["expected_processed_rows"] or any(
        r["source_sha256"] != manifest["sha256_uncompressed"] or r["survey_vintage"] != manifest["survey_vintage"]
        or r["wave"] != manifest["wave"] or r["retrieved_on"] != manifest["retrieved_on"] for r in rows
    ):
        raise ValueError("Processed metadata does not match the source manifest")
    write_csv(rows, output)
    print(f"Wrote {len(rows)} observed, unverified NFHS-5 indicator rows to {output}")
