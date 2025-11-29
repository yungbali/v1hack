"""
Resolve duplicate country-indicator-time observations in the fiscal dataset.

The script applies the due diligence specification by:
- Loading and standardising raw data via `fiscal_data_audit` helpers.
- Prioritising higher-frequency observations (Monthly > Quarterly > Yearly).
- Handling same-frequency conflicts with tolerance-based rules.
- Logging automated decisions and flagging rows that require manual review.
- Producing a deduplicated CSV for downstream analysis.

Run with:
    python scripts/resolve_fiscal_duplicates.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

import sys

CURRENT_DIR = Path(__file__).parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from fiscal_data_audit import clean_dataframe, load_raw_data  # type: ignore


BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DEDUPED_OUTPUT = PROCESSED_DIR / "fiscal_data_deduped.csv"
MANUAL_REVIEW_OUTPUT = PROCESSED_DIR / "fiscal_duplicates_manual_review.csv"
DUE_DILIGENCE_LOG = PROCESSED_DIR / "due_diligence_log.csv"

FREQUENCY_PRIORITY: Dict[str, int] = {"Monthly": 0, "Quarterly": 1, "Yearly": 2}
RELATIVE_DIFF_THRESHOLD = 0.01  # 1%


def resolve_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, str]]]:
    """Apply duplicate resolution rules and return cleaned data plus manual review cases."""
    df = df.copy()
    df["freq_rank"] = df["Frequency"].map(FREQUENCY_PRIORITY).fillna(3)
    df["abs_amount"] = df["Amount_numeric"].abs()
    df["row_id"] = df.index

    keep_indices: List[int] = []
    manual_cases: List[pd.Series] = []
    log_entries: List[Dict[str, str]] = []

    groups = df.groupby(["Country", "Indicator", "Time"], sort=False)

    for (country, indicator, timestamp), group in groups:
        if len(group) == 1:
            keep_indices.append(group.iloc[0]["row_id"])
            continue

        best_rank = group["freq_rank"].min()
        candidates = group[group["freq_rank"] == best_rank].copy()
        dropped = group[group["freq_rank"] > best_rank]

        decision_context = {
            "country": country,
            "indicator": indicator,
            "time": timestamp.isoformat() if pd.notna(timestamp) else "NA",
            "candidates": len(candidates),
            "dropped_lower_frequency": len(dropped),
        }

        if len(candidates) == 1:
            chosen = candidates.iloc[0]
            keep_indices.append(chosen["row_id"])
            log_entries.append(
                {
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "country": country,
                    "indicator": indicator,
                    "time": decision_context["time"],
                    "issue_type": "duplicate_frequency",
                    "action_taken": "Kept higher-frequency observation; removed lower-priority frequencies.",
                    "decision_owner": "GPT-5 Codex automation",
                    "evidence_link": str(DEDUPED_OUTPUT.name),
                    "notes": f"Dropped {decision_context['dropped_lower_frequency']} lower-frequency rows.",
                }
            )
            continue

        # Same frequency duplicates remain – evaluate spread
        values = candidates["Amount_numeric"]
        max_abs = candidates["abs_amount"].max()
        min_abs = candidates["abs_amount"].min()
        range_abs = max_abs - min_abs
        relative_diff = range_abs / max_abs if max_abs else 0

        chosen = candidates.loc[candidates["abs_amount"].idxmax()]
        keep_indices.append(chosen["row_id"])

        if relative_diff <= RELATIVE_DIFF_THRESHOLD:
            log_entries.append(
                {
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "country": country,
                    "indicator": indicator,
                    "time": decision_context["time"],
                    "issue_type": "duplicate_same_frequency",
                    "action_taken": (
                        "Values within 1% range; retained maximum absolute amount as representative."
                    ),
                    "decision_owner": "GPT-5 Codex automation",
                    "evidence_link": str(DEDUPED_OUTPUT.name),
                    "notes": (
                        f"Kept {chosen['Frequency']} record ({chosen['Amount_numeric']}); "
                        f"dropped {len(candidates) - 1} alternatives."
                    ),
                }
            )
        else:
            log_entries.append(
                {
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "country": country,
                    "indicator": indicator,
                    "time": decision_context["time"],
                    "issue_type": "duplicate_conflict",
                    "action_taken": (
                        "Retained maximum absolute value for provisional dataset; escalated for manual review."
                    ),
                    "decision_owner": "GPT-5 Codex automation",
                    "evidence_link": str(MANUAL_REVIEW_OUTPUT.name),
                    "notes": (
                        f"Relative difference {relative_diff:.2%} across {len(candidates)} "
                        f"{chosen['Frequency']} records."
                    ),
                }
            )
            manual_cases.append(
                candidates.assign(
                    relative_diff=relative_diff,
                    kept_row_id=chosen["row_id"],
                )
            )

    deduped = df.loc[keep_indices].drop(columns=["freq_rank", "abs_amount", "row_id"])
    manual_df = pd.concat(manual_cases, ignore_index=True) if manual_cases else pd.DataFrame()

    return deduped, manual_df, log_entries


def append_due_diligence_log(entries: List[Dict[str, str]]) -> None:
    """Append decision records to the due diligence log."""
    if not entries:
        return

    log_df = pd.DataFrame(entries)

    if DUE_DILIGENCE_LOG.exists():
        existing = pd.read_csv(DUE_DILIGENCE_LOG)
        combined = pd.concat([existing, log_df], ignore_index=True)
    else:
        combined = log_df

    combined.to_csv(DUE_DILIGENCE_LOG, index=False)


def main() -> None:
    """Execute the duplicate resolution workflow."""
    print("Loading raw fiscal dataset…")
    raw_df = load_raw_data()
    print(f"✓ Loaded {len(raw_df):,} rows")

    print("Standardising dataset…")
    cleaned_df = clean_dataframe(raw_df)
    print("✓ Cleaned fields; identifying duplicates")

    deduped_df, manual_df, log_entries = resolve_duplicates(cleaned_df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    deduped_df.to_csv(DEDUPED_OUTPUT, index=False)
    print(f"✓ Deduplicated dataset saved to {DEDUPED_OUTPUT}")

    if not manual_df.empty:
        manual_df.to_csv(MANUAL_REVIEW_OUTPUT, index=False)
        print(
            f"⚠ {len(manual_df)} records require manual review "
            f"(see {MANUAL_REVIEW_OUTPUT})"
        )
    else:
        if MANUAL_REVIEW_OUTPUT.exists():
            MANUAL_REVIEW_OUTPUT.unlink()
        print("✓ No manual review cases detected.")

    append_due_diligence_log(log_entries)
    print(f"✓ Logged {len(log_entries)} decisions to {DUE_DILIGENCE_LOG}")


if __name__ == "__main__":
    main()

