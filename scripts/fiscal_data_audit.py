"""
Utility script to audit and standardise the 10Alytics fiscal dataset.

The script performs the following steps:
1. Loads the single Excel source (`10Alytics Hackathon- Fiscal Data.xlsx`).
2. Cleans indicator labels and converts the `Amount` column to numeric values.
3. Normalises units (millions, billions, percentages, etc.) into comparable scales.
4. Derives temporal fields (Year, Month, Quarter) from the `Time` column.
5. Flags duplicate country-indicator-time observations and summarises missingness.
6. Writes a cleaned export and quality report for downstream analytics.

Run with:
    python scripts/fiscal_data_audit.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, List

import pandas as pd
from pandas.tseries.offsets import MonthEnd, QuarterEnd, YearEnd


BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "10Alytics Hackathon- Fiscal Data.xlsx"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CLEAN_OUTPUT = PROCESSED_DIR / "fiscal_data_clean.csv"
DUPLICATES_OUTPUT = PROCESSED_DIR / "fiscal_data_duplicates.csv"
REPORT_OUTPUT = PROCESSED_DIR / "fiscal_data_quality_report.json"
RESOLUTION_LOG_OUTPUT = PROCESSED_DIR / "fiscal_duplicate_resolution_log.csv"
MANUAL_REVIEW_OUTPUT = PROCESSED_DIR / "fiscal_duplicate_manual_review.csv"
VALIDATION_OUTPUT = PROCESSED_DIR / "fiscal_data_validation_issues.csv"


@dataclass(frozen=True)
class UnitSpec:
    """Representation of a normalised unit."""

    category: str
    multiplier: float
    note: Optional[str] = None


UNIT_MAP: Dict[str, UnitSpec] = {
    "billion": UnitSpec(category="currency_billions", multiplier=1.0),
    "billions": UnitSpec(category="currency_billions", multiplier=1.0),
    "million": UnitSpec(category="currency_billions", multiplier=1e-3),
    "millions": UnitSpec(category="currency_billions", multiplier=1e-3),
    "trillion": UnitSpec(category="currency_billions", multiplier=1e3),
    "percent": UnitSpec(category="percentage", multiplier=1.0, note="Value expressed in %"),
    "%": UnitSpec(category="percentage", multiplier=1.0, note="Value expressed in %"),
    "percentage": UnitSpec(category="percentage", multiplier=1.0, note="Value expressed in %"),
    "points": UnitSpec(category="index_points", multiplier=1.0),
    "point": UnitSpec(category="index_points", multiplier=1.0),
    "persons": UnitSpec(category="population_count", multiplier=1.0),
    "people": UnitSpec(category="population_count", multiplier=1.0),
    "usd": UnitSpec(category="currency_usd", multiplier=1.0),
}


def load_raw_data() -> pd.DataFrame:
    """Load the raw Excel data."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Expected dataset at {DATA_PATH} was not found.")

    return pd.read_excel(DATA_PATH, sheet_name="Data")


def _align_time(time_value: pd.Timestamp, frequency: str) -> pd.Timestamp:
    """Return a period-end timestamp based on the stated frequency."""
    if pd.isna(time_value):
        return pd.NaT

    freq = (frequency or "").strip().lower()

    if freq == "monthly":
        return time_value + MonthEnd(0)
    if freq == "quarterly":
        return time_value + QuarterEnd(0)
    if freq in {"yearly", "annual", "annually"}:
        return time_value + YearEnd(0)
    if freq in {"biannual", "semi-annual", "semiannual", "half-yearly"}:
        # Treat half-year as 6-month period ending
        # Determine if date corresponds to H1 or H2
        month = time_value.month
        if month <= 6:
            return (pd.Timestamp(time_value.year, 6, 30))
        return (pd.Timestamp(time_value.year, 12, 31))
    # Default: return original date
    return time_value


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard cleaning transformations."""
    cleaned = df.copy()

    # Normalise column names and string fields
    cleaned.columns = [col.strip() for col in cleaned.columns]
    cleaned["Indicator"] = cleaned["Indicator"].astype(str).str.strip()
    cleaned["Country"] = cleaned["Country"].astype(str).str.strip()
    cleaned["Source"] = cleaned["Source"].astype(str).str.strip()
    cleaned["Unit"] = cleaned["Unit"].astype(str).str.strip()

    # Convert Amount to numeric while preserving sign and decimals
    numeric_amount = (
        cleaned["Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(r"[^\d\.\-]", "", regex=True)
    )

    cleaned["Amount_numeric"] = pd.to_numeric(numeric_amount, errors="coerce")

    # Derive datetime parts
    cleaned["Time"] = pd.to_datetime(cleaned["Time"], errors="coerce")
    cleaned["Month"] = cleaned["Time"].dt.month
    cleaned["Quarter"] = cleaned["Time"].dt.quarter
    cleaned["Year_original"] = cleaned["Time"].dt.year

    # Infer frequency corrections for mislabelled yearly data
    freq_series = cleaned["Frequency"].astype(str).str.strip()
    cleaned["Frequency"] = freq_series

    yearly_mask = freq_series.str.lower() == "yearly"
    if yearly_mask.any():
        yearly_df = cleaned[yearly_mask].copy()
        yearly_df["Year_temp"] = yearly_df["Time"].dt.year

        def infer_frequency(months: set[int]) -> str:
            if not months:
                return "Yearly"
            month_set = set(months)
            if month_set.issubset({1}):
                return "Yearly"
            if month_set.issubset({1, 7}):
                return "Biannual"
            if month_set.issubset({1, 4, 7, 10}):
                return "Quarterly"
            if len(month_set) >= 6:
                return "Monthly"
            # Default to yearly when pattern unclear
            return "Yearly"

        inferred = (
            yearly_df.groupby(["Country", "Indicator", "Year_temp"])["Month"]
            .agg(lambda months: infer_frequency({m for m in months if pd.notna(m)}))
            .reset_index()
            .rename(columns={"Month": "Inferred_Frequency"})
        )

        for _, row in inferred.iterrows():
            year_val = row["Year_temp"]
            if pd.isna(year_val):
                continue
            new_freq = row["Inferred_Frequency"]
            if new_freq != "Yearly":
                mask = (
                    (cleaned["Country"] == row["Country"])
                    & (cleaned["Indicator"] == row["Indicator"])
                    & (cleaned["Year_original"] == year_val)
                    & (cleaned["Frequency"].str.lower() == "yearly")
                )
                cleaned.loc[mask, "Frequency"] = new_freq

    # Recompute frequency string after corrections
    cleaned["Frequency"] = cleaned["Frequency"].astype(str).str.strip()

    cleaned["Time_aligned"] = cleaned.apply(
        lambda row: _align_time(row["Time"], row.get("Frequency", "")), axis=1
    )
    cleaned["Year"] = cleaned["Time_aligned"].dt.year
    cleaned = cleaned.drop(columns=["Year_original"])

    # Map units into standard categories
    cleaned["Unit_key"] = cleaned["Unit"].str.lower().str.strip()
    cleaned["Unit_category"] = cleaned["Unit_key"].map(
        lambda x: UNIT_MAP.get(x).category if x in UNIT_MAP else "unknown"
    )
    cleaned["Unit_multiplier"] = cleaned["Unit_key"].map(
        lambda x: UNIT_MAP.get(x).multiplier if x in UNIT_MAP else 1.0
    )
    cleaned["Amount_standardised"] = cleaned["Amount_numeric"] * cleaned["Unit_multiplier"]

    # For percentages retain both % and fractional representation
    cleaned["Amount_fraction"] = cleaned.apply(
        lambda row: (row["Amount_numeric"] / 100)
        if row["Unit_category"] == "percentage"
        else None,
        axis=1,
    )

    # Flag duplicates at the country-indicator-time grain
    key_cols = ["Country", "Indicator", "Frequency", "Time_aligned"]
    cleaned["is_duplicate"] = cleaned.duplicated(subset=key_cols, keep=False)

    return cleaned


def resolve_duplicate_records(
    cleaned: pd.DataFrame,
    tolerance: float = 0.01,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Resolve duplicate records where the spread between values is within tolerance.

    Args:
        cleaned: DataFrame after base cleaning.
        tolerance: Relative spread threshold (e.g., 0.01 = 1%) for automatic resolution.

    Returns:
        Tuple containing:
            - DataFrame with duplicates resolved where possible.
            - Resolution log DataFrame for automatically handled cases.
            - Manual review DataFrame listing unresolved duplicates.
    """
    key_cols = ["Country", "Indicator", "Frequency", "Time_aligned"]

    df = cleaned.copy()
    df["RowID"] = df.index

    duplicates = df[df.duplicated(subset=key_cols, keep=False)].copy()
    if duplicates.empty:
        df = df.drop(columns=["RowID"])
        df["is_duplicate"] = False
        return df, pd.DataFrame(), pd.DataFrame()

    drop_ids: List[int] = []
    resolution_logs: List[Dict[str, object]] = []
    manual_logs: List[Dict[str, object]] = []

    for key, group in duplicates.groupby(key_cols, sort=False):
        non_null = group.dropna(subset=["Amount_numeric"])

        if non_null.empty:
            manual_logs.append(
                {
                    "Country": key[0],
                    "Indicator": key[1],
                    "Frequency": key[2],
                    "Time_aligned": key[3],
                    "issue": "all_values_null",
                    "spread": None,
                    "relative_spread": None,
                    "values": [],
                    "row_ids": group["RowID"].tolist(),
                }
            )
            continue

        values = non_null["Amount_numeric"].astype(float)
        max_val = values.max()
        min_val = values.min()
        spread = abs(max_val - min_val)
        median = values.median()
        if median == 0:
            relative_spread = 0.0 if spread == 0 else float("inf")
        else:
            relative_spread = spread / abs(median)

        if relative_spread <= tolerance:
            # Keep the latest timestamp with non-null amount
            selected = (
                non_null.sort_values(["Time", "Amount_numeric"], ascending=[True, False]).iloc[-1]
            )
            keep_id = int(selected["RowID"])
            drop_group = group[group["RowID"] != keep_id]
            drop_ids.extend(drop_group["RowID"].tolist())
            resolution_logs.append(
                {
                    "Country": key[0],
                    "Indicator": key[1],
                    "Frequency": key[2],
                    "Time_aligned": key[3],
                    "kept_row_id": keep_id,
                    "kept_time": selected["Time"],
                    "kept_amount": selected["Amount_numeric"],
                    "dropped_row_ids": drop_group["RowID"].tolist(),
                    "dropped_count": len(drop_group),
                    "spread": spread,
                    "relative_spread": relative_spread,
                    "resolution": "auto_low_spread",
                }
            )
        else:
            manual_logs.append(
                {
                    "Country": key[0],
                    "Indicator": key[1],
                    "Frequency": key[2],
                    "Time_aligned": key[3],
                    "issue": "spread_exceeds_tolerance",
                    "spread": spread,
                    "relative_spread": relative_spread,
                    "values": sorted(values.unique().tolist()),
                    "row_ids": group["RowID"].tolist(),
                }
            )

    if drop_ids:
        df = df.drop(index=drop_ids)

    df = df.drop(columns=["RowID"])
    df["is_duplicate"] = df.duplicated(subset=key_cols, keep=False)

    resolution_df = pd.DataFrame(resolution_logs)
    manual_df = pd.DataFrame(manual_logs)

    return df, resolution_df, manual_df


def run_validation_checks(cleaned: pd.DataFrame) -> pd.DataFrame:
    """
    Apply validation rules and return issue records.

    Returns:
        DataFrame with columns: issue_type, country, indicator, frequency, time_aligned, details
    """

    issues: List[Dict[str, object]] = []

    # Unknown unit categories
    unknown_units = cleaned[cleaned["Unit_category"] == "unknown"]
    for _, row in unknown_units.iterrows():
        issues.append(
            {
                "issue_type": "unknown_unit",
                "country": row["Country"],
                "indicator": row["Indicator"],
                "frequency": row["Frequency"],
                "time_aligned": row["Time_aligned"],
                "details": f"Unit '{row['Unit']}' not mapped",
            }
        )

    # Percentage range checks
    percentage_rules = {
        "Inflation Rate": (-10, 200),
        "Food Inflation": (-20, 200),
        "Food Inflation YoY": (-50, 200),
        "Interest Rate": (0, 100),
        "Unemployment Rate": (0, 70),
        "GDP Growth Rate": (-20, 50),
    }

    pct_df = cleaned[
        cleaned["Indicator"].isin(percentage_rules.keys())
        & cleaned["Amount_numeric"].notna()
    ]
    for indicator, (low, high) in percentage_rules.items():
        subset = pct_df[pct_df["Indicator"] == indicator]
        outliers = subset[(subset["Amount_numeric"] < low) | (subset["Amount_numeric"] > high)]
        for _, row in outliers.iterrows():
            issues.append(
                {
                    "issue_type": "range_violation",
                    "country": row["Country"],
                    "indicator": row["Indicator"],
                    "frequency": row["Frequency"],
                    "time_aligned": row["Time_aligned"],
                    "details": f"Value {row['Amount_numeric']} outside [{low}, {high}]",
                }
            )

    # Debt-to-GDP ratio checks
    debt_df = cleaned[cleaned["Indicator"] == "Government Debt"][
        ["Country", "Time_aligned", "Amount_standardised"]
    ].rename(columns={"Amount_standardised": "Debt"})
    gdp_df = cleaned[cleaned["Indicator"] == "Nominal GDP"][
        ["Country", "Time_aligned", "Amount_standardised"]
    ].rename(columns={"Amount_standardised": "GDP"})

    debt_gdp = debt_df.merge(gdp_df, on=["Country", "Time_aligned"], how="inner")
    debt_gdp = debt_gdp[(debt_gdp["Debt"].notna()) & (debt_gdp["GDP"].notna()) & (debt_gdp["GDP"] != 0)]
    debt_gdp["Debt_to_GDP"] = debt_gdp["Debt"] / debt_gdp["GDP"]
    debt_ratio_issues = debt_gdp[debt_gdp["Debt_to_GDP"] > 4]
    for _, row in debt_ratio_issues.iterrows():
        issues.append(
            {
                "issue_type": "debt_to_gdp_outlier",
                "country": row["Country"],
                "indicator": "Government Debt",
                "frequency": "Derived",
                "time_aligned": row["Time_aligned"],
                "details": f"Debt-to-GDP ratio {row['Debt_to_GDP']:.2f} exceeds threshold 4.0",
            }
        )

    # Missing recent observations for priority indicators
    priority_countries = {"Nigeria", "South Africa", "Egypt", "Kenya", "Ghana"}
    priority_indicators = ["Revenue", "Budget Deficit/Surplus", "Inflation Rate"]

    freq_rank = {
        "Monthly": 1,
        "Quarterly": 2,
        "Biannual": 3,
        "Semi-Annual": 3,
        "Semiannual": 3,
        "Half-Yearly": 3,
        "Yearly": 4,
    }

    for indicator in priority_indicators:
        subset = cleaned[cleaned["Indicator"] == indicator]
        if subset.empty:
            continue
        max_time = subset["Time_aligned"].max()
        if pd.isna(max_time):
            continue
        for country in priority_countries:
            country_subset = subset[subset["Country"] == country]
            if country_subset.empty:
                issues.append(
                    {
                        "issue_type": "missing_series",
                        "country": country,
                        "indicator": indicator,
                        "frequency": None,
                        "time_aligned": None,
                        "details": "No records available",
                    }
                )
                continue
            country_time = country_subset["Time_aligned"].max()
            country_freq = country_subset["Frequency"].dropna().map(lambda x: freq_rank.get(str(x), 5)).min()
            if pd.isna(country_time):
                continue
            lag_days = (max_time - country_time).days
            threshold_days = 180 if country_freq and country_freq <= 2 else 730
            if lag_days > threshold_days:
                issues.append(
                    {
                        "issue_type": "stale_series",
                        "country": country,
                        "indicator": indicator,
                        "frequency": country_subset.sort_values("Time_aligned", ascending=False).iloc[0]["Frequency"],
                        "time_aligned": country_time,
                        "details": f"Latest observation lags {lag_days} days behind dataset maximum {max_time.date()}",
                    }
                )

    return pd.DataFrame(issues)
def generate_quality_report(cleaned: pd.DataFrame) -> Dict[str, object]:
    """Compose a dictionary with data quality diagnostics."""
    rows_before = len(cleaned)
    duplicates = cleaned[cleaned["is_duplicate"]]
    duplicate_summary = (
        duplicates.groupby(["Country", "Indicator"])
        .size()
        .reset_index(name="duplicate_count")
        .sort_values("duplicate_count", ascending=False)
        .head(20)
        .to_dict(orient="records")
    )

    missing_summary = (
        cleaned.isna().mean().sort_values(ascending=False).round(4).to_dict()
    )
    unit_mix = (
        cleaned["Unit_category"]
        .value_counts(dropna=False)
        .to_dict()
    )

    country_coverage = cleaned["Country"].nunique()
    indicator_coverage = cleaned["Indicator"].nunique()
    year_min = int(cleaned["Year"].min()) if pd.notna(cleaned["Year"].min()) else None
    year_max = int(cleaned["Year"].max()) if pd.notna(cleaned["Year"].max()) else None

    report = {
        "rows": rows_before,
        "countries": country_coverage,
        "indicators": indicator_coverage,
        "year_min": year_min,
        "year_max": year_max,
        "unit_category_distribution": unit_mix,
        "missing_value_share": missing_summary,
        "duplicate_records_flagged": len(duplicates),
        "duplicate_sample": duplicate_summary,
        "notes": [
            "Amount_standardised expresses currency values in billions of local currency.",
            "Amount_fraction provides decimal form for percentage indicators.",
            "Rows flagged as duplicates share the same country, indicator, frequency, and aligned timestamp.",
        ],
    }

    return report


def persist_outputs(
    cleaned: pd.DataFrame,
    report: Dict[str, object],
    resolution_log: pd.DataFrame,
    manual_review: pd.DataFrame,
    validation_issues: pd.DataFrame,
) -> None:
    """Write cleaned data, duplicate listings, and report to disk."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(CLEAN_OUTPUT, index=False)

    duplicates = cleaned[cleaned["is_duplicate"]]
    if not duplicates.empty:
        duplicates.sort_values(["Country", "Indicator", "Frequency", "Time_aligned"]).to_csv(
            DUPLICATES_OUTPUT, index=False
        )
    else:
        DUPLICATES_OUTPUT.write_text("")

    if not resolution_log.empty:
        resolution_log.to_csv(RESOLUTION_LOG_OUTPUT, index=False)
    else:
        RESOLUTION_LOG_OUTPUT.write_text("")

    if not manual_review.empty:
        manual_review.to_csv(MANUAL_REVIEW_OUTPUT, index=False)
    else:
        MANUAL_REVIEW_OUTPUT.write_text("")

    if not validation_issues.empty:
        validation_issues.to_csv(VALIDATION_OUTPUT, index=False)
    else:
        VALIDATION_OUTPUT.write_text("")

    REPORT_OUTPUT.write_text(json.dumps(report, indent=2))


def main() -> None:
    """Run the audit pipeline."""
    print("Loading fiscal dataset…")
    raw_df = load_raw_data()
    print(f"✓ Loaded {len(raw_df):,} rows with {raw_df.shape[1]} columns")

    print("Cleaning and normalising fields…")
    cleaned_df = clean_dataframe(raw_df)
    print("✓ Added numeric, unit, and temporal fields")

    print("Resolving duplicate records where safe…")
    resolved_df, resolution_log, manual_review = resolve_duplicate_records(cleaned_df)
    print(
        f"✓ Automatically resolved {len(resolution_log)} duplicate groups; "
        f"{len(manual_review)} groups pending manual review"
    )

    print("Running validation checks…")
    validation_issues = run_validation_checks(resolved_df)
    print(f"✓ Validation issues logged: {len(validation_issues)}")

    print("Generating quality diagnostics…")
    quality_report = generate_quality_report(resolved_df)
    quality_report["duplicate_groups_auto_resolved"] = int(len(resolution_log))
    quality_report["duplicate_groups_manual_review"] = int(len(manual_review))
    quality_report["validation_issue_count"] = int(len(validation_issues))
    print(
        f"✓ Dataset spans {quality_report['countries']} countries, "
        f"{quality_report['indicators']} indicators, "
        f"{quality_report['year_min']}–{quality_report['year_max']}"
    )
    print(
        f"✓ Remaining duplicate rows flagged for manual review: "
        f"{quality_report['duplicate_records_flagged']}"
    )

    print("Persisting cleaned outputs and report…")
    persist_outputs(resolved_df, quality_report, resolution_log, manual_review, validation_issues)
    print(f"✓ Cleaned data saved to {CLEAN_OUTPUT}")
    if quality_report["duplicate_records_flagged"]:
        print(f"⚠ Manual review required — see {DUPLICATES_OUTPUT}")
    print(f"✓ Quality report written to {REPORT_OUTPUT}")
    print("Audit complete.")


if __name__ == "__main__":
    main()

