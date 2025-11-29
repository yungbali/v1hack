# Fiscal Insight Deck Wireframe

Primary audience: senior policymakers and business leaders seeking actionable guidance on African fiscal stability.  
Primary dataset: `10Alytics Hackathon- Fiscal Data.xlsx` (audited via `python scripts/fiscal_data_audit.py`, outputs in `data/processed/`).

## Slide Flow

- **Cover & Mandate** – Reiterate hackathon brief, SDG linkage, and data provenance.
- **Executive Snapshot** – Three headline risks/opportunities with quantified impact.
- **Data Quality & Methodology** – Cleaning steps, duplicate handling notes, key limitations/enrichment roadmap.
- **Historical Budget Balance Trends** – Cross-country heatmap + rolling average to satisfy “build visualizations” ask.
- **Drivers of Fiscal Instability** – Waterfall for Nigeria + comparative bar for peer group (revenue vs. expenditure shocks).
- **Fiscal Stress Scorecard** – Composite index (debt/GDP, deficit/revenue, revenue/GDP, inflation, trade balance) with traffic-light coding.
- **Risk Radar & Anomaly Alerts** – Scatter/bullet charts highlighting outliers (e.g., South Africa debt load, inflation decelerations).
- **Forward Look (Predictive)** – Forecast fan chart for deficit & inflation for top-5 economies with scenario toggles.
- **Action Playbook** – Recommendation matrix (policy lever, SDG, business implication, lead agency).
- **Next Steps & Data Gaps** – Limitations, enrichment wishlist, partnership asks.

## Visual Details

### Historical Budget Balance Heatmap

- **Type:** Diverging heatmap (countries vs. year).
- **Data:** `Budget Deficit/Surplus` (currency_billions), aggregated to yearly mean using cleaned dataset.
- **Insight:** Surface persistent deficits vs. consolidation episodes; annotate with macro events.
- **Action Prompt:** “Target fiscal consolidation in countries with >60% deficit-to-revenue over past 3 yrs.”

### Revenue & Expenditure Dynamics

- **Type:** Dual-axis line (rolling 12-month sum) + variance bar.
- **Data:** `Revenue`, `Expenditure`, `Capital Expenditure` (billions); deduplicated monthly series.
- **Insight:** Show revenue volatility and spending spikes; connect to SDG financing gaps.
- **Action Prompt:** “Institute quarterly expenditure reviews; accelerate VAT compliance drive.”

### Fiscal Stress Scorecard

- **Type:** Radar chart (per country) + supporting bar table.
- **Metrics:** Debt/GDP, Deficit/Revenue, Revenue/GDP, Tax-to-Revenue, Inflation YoY, Trade Balance (% GDP).
- **Computation:** Derived from `fiscal_data_clean.csv`; thresholds set in upcoming scorecard task.
- **Insight:** Quickly flag countries in red zone for immediate policy dialogue.

### Risk & Anomaly Radar

- **Type:** Scatter plot (Debt/GDP vs. Revenue/GDP) with bubble size = deficit share; highlight anomalies.
- **Data:** Same ratios as scorecard; filter latest available year per country.
- **Insight:** Emphasise South Africa’s leverage, Kenya’s external gap, Nigeria’s deficit pressure.
- **Action Prompt:** Policy-specific callouts (debt reprofiling, export diversification, expenditure sequencing).

### Inflation & Monetary Pulse

- **Type:** Fan chart + YoY column for Inflation Rate; overlay interest-rate policy band.
- **Data:** Monthly inflation, interest rate, CPI (percentage & index); forecasting window 12 months.
- **Insight:** Communicate deceleration and space for policy recalibration; highlight risk of reversal.
- **Action Prompt:** “Deploy targeted food security buffers; calibrate interest rate path to sustain disinflation.”

### Trade Balance Dashboard

- **Type:** Waterfall (exports–imports contribution) + map shading by surplus/deficit.
- **Data:** Latest 24-month exports/imports, converted to billions.
- **Insight:** Identify surplus economies (Nigeria, South Africa) vs. deficit (Kenya, Egypt); link to industrial policy.
- **Action Prompt:** “Scale agro-processing incentives, address FX bottlenecks for import-dependent economies.”

### Recommendation Matrix

- **Type:** Structured table (Country | Challenge | Policy Lever | SDG Impact | Business Action | Lead Agency).
- **Data:** Synthesised from stress scorecard + qualitative context.
- **Insight:** Provide ready-to-implement playbook; ensures presentation meets “propose actionable recommendations.”

## Data & Design Notes

- Use `Amount_standardised` (billions) for currency visuals; retain `Amount_fraction` for percentage-based charts.
- Duplicates flagged in `data/processed/fiscal_data_duplicates.csv` must be resolved (choose authoritative source or aggregate) before charting.
- Missing social-spend data (health, education) should be caveated on relevant slides; plan enrichment via ministry reports or World Bank.
- Adopt consistent colour logic: surplus/positive in navy/teal; deficits/risks in amber/crimson; neutral in grey.
- Include SDG iconography on each slide where applicable to reinforce alignment with hackathon objectives.

## Outstanding Items Before Visual Build

1. Finalise duplicate-resolution strategy (averaging vs. authoritative override).
2. Confirm threshold definitions for scorecard traffic lights.
3. Produce dataset extracts per visualization (stored in `/data/processed/` as CSV).
4. Draft speaker notes aligning key numbers to policy/business actions.
