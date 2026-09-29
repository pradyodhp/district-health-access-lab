"""Rebuild the selected pilot extract from the versioned raw source."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from health_access.extract import extract, write_csv  # noqa: E402

if __name__ == "__main__":
    output = ROOT / "data/processed/pilot_indicators.csv"
    rows = extract(ROOT / "data/raw/nfhs_india_2026-09-30.csv.gz")
    write_csv(rows, output)
    print(f"Wrote {len(rows)} observed, unverified NFHS-5 indicator rows to {output}")
