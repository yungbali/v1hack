# Fiscal Data Due Diligence Specification

## Objectives

- Guarantee the `10Alytics Hackathon- Fiscal Data.xlsx` source is reproducibly cleaned and audit-ready before insight generation.
- Provide transparent rules for deduplication, validation, anomaly flagging, and documentation so policy and business stakeholders can trust every number.
- Produce artefacts that downstream teams (visualisation, modelling, communications) can confidently reuse without revalidating raw inputs.

## Scope & Inputs

- **Primary input:** `10Alytics Hackathon- Fiscal Data.xlsx` (sheet: `Data`).
- **Audit pipeline:** `python scripts/fiscal_data_audit.py` (creates `data/processed/fiscal_data_clean.csv`, `fiscal_data_duplicates.csv`, `fiscal_data_quality_report.json`).
- **Downstream artefacts:** `fiscal_stress_scorecard.csv`, dashboard extracts, presentation visuals.

## Processing Workflow

1. **Ingest & Normalise**

   - Trim column names and string fields (`Country`, `Indicator`, `Unit`, `Source`).
   - Convert `Amount` to numeric (`Amount_numeric`) by removing thousand separators and stray characters.
   - Derive `Time` (datetime), `Year`, `Month`, `Quarter`.
   - Map units into standard categories with multipliers; compute `Amount_standardised` (billions of local currency) and `Amount_fraction` (decimal for percentages).

2. **Deduplication Strategy**

   - Grain: (`Country`, `Indicator`, `Time`).
   - Initial flagging: rows where duplicates exist are exported to `fiscal_data_duplicates.csv`.
   - **Priority queue:** Nigeria (Revenue, Expenditure, Budget Deficit/Surplus, Imports, Exports), Kenya (Imports/Exports), South Africa (GDP series), Rwanda (trade data).
   - **Resolution rules:**
     1. Prefer entries from official fiscal sources (e.g., national treasury, IMF) if `Source` differs.
     2. When duplicate amounts differ by ≤1%, keep the most recent ingestion (`Time` closest to actual period end) and log rationale.
     3. If values differ materially (>1%) and source is identical, escalate for manual verification; record decision in due diligence log.
     4. Archive discarded rows in `/data/processed/archive/YYYYMMDD_country_indicator.csv`.
   - After resolution, re-run audit pipeline and confirm `duplicate_records_flagged == 0` before publishing visuals.

3. **Validation & Rules**

   - **Unit Consistency:** ensure indicators tagged as `currency_billions`/`percentage` align with known unit lists; flag `Unit_category == "unknown"`.
   - **Range Checks:**
     - `Debt_to_GDP` derived ratio must fall within 0–4; values outside raise a `critical` flag.
     - `Inflation Rate` between -10% and 200%; `Interest Rate` between 0% and 100%.
     - `Revenue`, `Expenditure`, `Capital Expenditure`, `Budget Deficit/Surplus` cannot be NaN when `Frequency` is monthly or quarterly for top-five economies (Nigeria, South Africa, Egypt, Kenya, Ghana); missing entries flagged `major`.
   - **Temporal Gaps:** highlight gaps >6 months for high-frequency indicators (monthly revenue/deficit, inflation) and >2 years for annual indicators (GDP, debt, unemployment).
   - **Trend Outliers:** apply rolling z-score (window 12 for monthly, 5 for annual); values with |z| > 3 recorded as anomalies.

4. **Quality Reporting**

   - Extend `fiscal_data_quality_report.json` with:
     - Counts of unresolved duplicates per indicator.
     - Unit consistency breaches.
     - Range and trend anomaly summaries.
     - Missingness by indicator-country pair.
     - Counts of duplicate groups auto-resolved vs. pending manual review.
     - Total validation issue count.
   - Generate tabular `fiscal_data_quality_report.md` for human-readable briefing (auto-export from notebook).
   - Persist companion artefacts with every audit cycle:
     - `fiscal_duplicate_resolution_log.csv`
     - `fiscal_duplicate_manual_review.csv`
     - `fiscal_data_validation_issues.csv`

5. **Documentation & Logging**
   - Maintain `data/due_diligence_log.csv` with columns: `date`, `country`, `indicator`, `issue_type`, `action_taken`, `decision_owner`, `evidence_link`.
   - Update `FISCAL_STRESS_SCORECARD.md` commentary whenever a data decision materially alters ratios.
   - Archive raw snapshots (`data/raw/YYYYMMDD_fiscal_data.csv`) before each reconciliation iteration for rollback.
   - Ensure manual review tracker and validation issues accompany the clean dataset release.

## Deliverables & Acceptance Criteria

- `fiscal_data_clean.csv` free of duplicate (`Country`, `Indicator`, `Time`) rows.
- Validation report documenting zero `critical` issues; `major` issues explicitly acknowledged with mitigation timeline.
- Due diligence log populated for all manual interventions.
- Quality report, manual review tracker, resolution log, and validation issues reviewed/approved before dashboards or presentation slides are refreshed.

## Open Considerations

- Integrate external data sources (World Bank, IMF) for indicators with structural gaps (health, education, debt for Botswana/Senegal).
- Decide on automated vs. manual reconciliation tooling (e.g., Great Expectations, Pandera) once basic rule set is stable.
- Align publication cadence with policy briefing schedule (e.g., monthly refresh aligned with fiscal releases).
