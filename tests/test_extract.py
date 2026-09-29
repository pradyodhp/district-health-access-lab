import csv
import gzip
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from health_access.extract import INDICATORS, PILOT_DISTRICTS, extract, write_csv

RAW = ROOT / "data/raw/nfhs_india_2026-09-30.csv.gz"


def test_pilot_coverage_and_lineage():
    rows = extract(RAW)
    assert len(rows) == len(PILOT_DISTRICTS) * len(INDICATORS)
    assert len({(r["state"], r["district"], r["indicator_id"]) for r in rows}) == len(rows)
    assert all(r["value_status"] == "OBSERVED_UNVERIFIED" and r["wave"] == "NFHS-5" for r in rows)
    assert all(0 <= float(r["value_pct"]) <= 100 for r in rows)
    assert len({r["source_sha256"] for r in rows}) == 1


def test_known_source_row_not_diagnosis():
    row = next(r for r in extract(RAW) if (r["state"], r["district"], r["indicator_id"]) ==
               ("Maharashtra", "Pune", "glucose_elevated_or_medicine_female"))
    assert row["value_pct"] == "12.3"
    assert "not diagnosis" in row["caveat"]


def _fixture(tmp_path, *, value="12.3", duplicate=False, missing=False):
    with gzip.open(RAW, "rt", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
        fields = list(rows[0])
    match = next(x for x in rows if (x["State"], x["District"], x["Indicator"]) ==
                 ("Maharashtra", "Pune", next(iter(INDICATORS))))
    match["NFHS 5"] = value
    if duplicate:
        rows.append(match.copy())
    if missing:
        rows.remove(match)
    path = tmp_path / "test.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.mark.parametrize("value", ["101", "-1", "n/a", ""])
def test_invalid_value_fails_closed(tmp_path, value):
    with pytest.raises(ValueError):
        extract(_fixture(tmp_path, value=value))


@pytest.mark.parametrize("change", ["duplicate", "missing"])
def test_duplicate_or_missing_row_fails_closed(tmp_path, change):
    with pytest.raises(ValueError):
        extract(_fixture(tmp_path, **{change: True}))


def test_round_trip(tmp_path):
    path = tmp_path / "out.csv"
    write_csv(extract(RAW), path)
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 24
    assert all(row["source_url"].startswith("https://") for row in rows)
