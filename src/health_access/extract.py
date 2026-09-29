"""Strict, dependency-free extraction of selected NFHS district fact-sheet rows.

The community CSV is not an official or independently validated source. This module
retains exact indicator labels and refuses incomplete or ambiguous pilot extracts.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/SaiSiddhardhaKalla/NFHS/main/India.csv"
RETRIEVED_ON = "2026-09-30"
PILOT_DISTRICTS = (
    ("Maharashtra", "Mumbai"),
    ("Maharashtra", "Pune"),
    ("Maharashtra", "Gadchiroli"),
    ("Odisha", "Khordha"),
    ("Odisha", "Koraput"),
    ("Odisha", "Malkangiri"),
)
INDICATORS = {
    "Female Blood sugar level  high or very high (>140 mg/dl) or taking medicine to control blood sugar level (%)": ("glucose_elevated_or_medicine_female", "female"),
    "Male Blood sugar level  high or very high (>140 mg/dl) or taking medicine to control blood sugar level (%)": ("glucose_elevated_or_medicine_male", "male"),
    "Female Elevated blood pressure or taking medicine to control blood pressure (%)": ("bp_elevated_or_medicine_female", "female"),
    "Male Elevated blood pressure or taking medicine to control blood pressure (%)": ("bp_elevated_or_medicine_male", "male"),
}
FIELDS = (
    "state", "district", "state_census_code", "district_census_code",
    "indicator_id", "indicator_label", "sex", "age_group", "wave",
    "survey_vintage", "value_pct", "value_status", "source_url",
    "source_sha256", "retrieved_on", "caveat",
)


def extract(raw_path: Path) -> list[dict[str, str]]:
    """Extract six districts x four NFHS-5 indicators; fail closed on data drift."""
    with gzip.open(raw_path, "rb") as stream:
        raw_bytes = stream.read()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    import io
    reader = csv.DictReader(io.StringIO(raw_bytes.decode("utf-8-sig")))
    expected_columns = {"State", "ST_CEN_CD", "District", "DT_CEN_CD", "Indicator", "NFHS 5"}
    if not expected_columns.issubset(reader.fieldnames or []):
        raise ValueError(f"Missing columns: {expected_columns - set(reader.fieldnames or [])}")
    selected: dict[tuple[str, str, str], dict[str, str]] = {}
    for source in reader:
        district_key = (source["State"], source["District"])
        label = source["Indicator"]
        if district_key not in PILOT_DISTRICTS or label not in INDICATORS:
            continue
        indicator_id, sex = INDICATORS[label]
        key = (*district_key, indicator_id)
        if key in selected:
            raise ValueError(f"Duplicate district indicator: {key}")
        raw_value = source["NFHS 5"].strip()
        if not raw_value:
            raise ValueError(f"Missing NFHS-5 value: {key}")
        try:
            numeric = float(raw_value)
        except ValueError as exc:
            raise ValueError(f"Invalid percentage for {key}: {raw_value!r}") from exc
        if not 0 <= numeric <= 100:
            raise ValueError(f"Percentage out of bounds for {key}: {numeric}")
        selected[key] = {
            "state": district_key[0], "district": district_key[1],
            "state_census_code": source["ST_CEN_CD"],
            "district_census_code": source["DT_CEN_CD"],
            "indicator_id": indicator_id, "indicator_label": label,
            "sex": sex, "age_group": "15+", "wave": "NFHS-5",
            "survey_vintage": "2019-21", "value_pct": raw_value,
            "value_status": "OBSERVED_UNVERIFIED", "source_url": SOURCE_URL,
            "source_sha256": digest, "retrieved_on": RETRIEVED_ON,
            "caveat": "Elevated measure or medicine; not diagnosis or screening coverage. Official PDF cross-check pending.",
        }
    expected = {(s, d, i) for s, d in PILOT_DISTRICTS for i, _ in INDICATORS.values()}
    missing = expected - selected.keys()
    if missing:
        raise ValueError(f"Missing {len(missing)} pilot rows: {sorted(missing)}")
    return [selected[key] for key in sorted(selected)]


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
