## Fiscal Stress Scorecard Overview

- Source dataset: `data/processed/fiscal_data_clean.csv` (generated via `scripts/fiscal_data_audit.py`).
- Scorecard export: `data/processed/fiscal_stress_scorecard.csv` (generated 2025-11-29).
- Indicators harmonised to billions of local currency; percentages retain headline value with decimal companion where needed.
- Thresholds applied:
  - `Debt_to_GDP`: green ≤60%, amber ≤90%, red >90%.
  - `Deficit_to_Revenue`: green ≤30%, amber ≤60%, red >60%.
  - `Revenue_to_GDP`: green ≥25%, amber ≥18%, red <18%.
  - `Inflation_pct`: green ≤10%, amber ≤20%, red >20%.
  - `Trade_Balance_to_GDP`: green ≥0, amber ≥-5%, red <-5%.

### Snapshot of Priority Countries

| Country | Debt/GDP | Deficit/Revenue | Revenue/GDP | Inflation | Trade Balance/GDP | Key Callout |
|---------|----------|-----------------|-------------|-----------|-------------------|-------------|
| Nigeria | **Red** (178%) | **Red** (239%) | **Red** (1.1%) | **Red** (20.1%) | Green (+2.45%) | Persistent double-digit deficits despite trade surplus; revenue mobilisation urgent. |
| South Africa | **Red** (300%) | Green (1%) | **Red** (10.4%) | Green (2.8%) | Green (+1.31%) | Debt load extreme relative to GDP; revenue-to-GDP structurally weak. |
| Egypt | Green (2.3%) | **Red** (107%) | **Red** (11.2%) | Amber (13.9%) | Amber (-0.4%) | Primary risk is deficit dependence amid moderate inflation. |
| Ghana | Green (19%) | Amber (41.6%) | **Red** (5.4%) | Green (9.4%) | Green (+0.02%) | Revenue base thin; deficit share manageable but needs monitoring. |
| Kenya | Data Gap | Data Gap | Green (39.4%) | Green (3.7%) | Amber (-3.5%) | Revenue effort solid; trade gap pressures FX—need debt data confirmation. |

> Full country list and raw ratios available in `fiscal_stress_scorecard.csv`. Several countries (Botswana, Senegal, Algeria) require debt or revenue data enrichment before scoring.

### Data Limitations & Next Steps
- 2,266 duplicate country-indicator-time rows remain flagged for manual reconciliation (`data/processed/fiscal_data_duplicates.csv`). Prioritise high-impact series (Nigeria fiscal flows, Kenya trade) for verification.
- Debt data missing for multiple countries; liaise with finance ministries or multilateral datasets before public release.
- Inflation YoY changes cannot be computed everywhere due to sparse historical coverage—supplement with national statistical bulletins.

## Policy & Business Recommendation Matrix

| Country | Stress Signals | Policy Levers | SDG Linkage | Business Implications | Lead Stakeholders |
|---------|----------------|---------------|-------------|------------------------|-------------------|
| Nigeria | Red on debt, deficit, revenue effort, inflation; green trade surplus. | Enforce VAT/compliance drive, broaden petroleum royalties, phase non-priority capex, institute quarterly cash management councils. | SDG 8 (growth), SDG 16 (institutions), SDG 3 (health funding). | Tighten working-capital buffers; hedge FX exposure; prioritise partnerships in high-multiplier infrastructure and agri-processing. | Federal Ministry of Finance, FIRS, Budget Office, CBN. |
| South Africa | Debt-to-GDP >300%, weak revenue capture, moderate inflation. | Launch debt reprofiling strategy, expand tax base (digital economy, illicit flows), accelerate PPPs for infrastructure to free fiscal space. | SDG 9 (infrastructure), SDG 16 (transparency). | Reassess sovereign exposure; pursue blended-finance PPPs; expect tighter procurement scrutiny. | National Treasury, SARS, Infrastructure SA. |
| Egypt | Strong GDP vs. low revenue, high deficit, inflation amber, mild trade deficit. | Rationalise subsidies, expand property/consumption taxes, targeted FX support for exporters, strengthen fiscal transparency. | SDG 8 (decent work), SDG 12 (responsible consumption). | Businesses should anticipate subsidy rationalisation; diversify funding currency mix. | Ministry of Finance, CBE, General Authority for Investment. |
| Ghana | Low debt ratio but thin revenue base; inflation retreating. | Scale e-VAT rollout, formalise informal sector, ringfence growth capex, deepen local capital markets. | SDG 8, SDG 9. | Expand local sourcing to tap incentives; prepare for widened tax net. | Ministry of Finance, GRA, BoG. |
| Kenya | Revenue/GDP strong, trade deficit amber, debt data missing. | Audit debt registers, prioritise export diversification (horticulture, tech services), enhance FX reserves buffers. | SDG 8, SDG 9. | Exporters should pursue value-add upgrades; importers hedge against FX swings. | National Treasury, CBK, Export Promotion Council. |
| Tanzania | Red on deficit/revenue, revenue/gdp weak, trade amber. | Implement fiscal rules to cap deficit, modernise tax administration, focus capex on logistics corridors, improve SOE governance. | SDG 9, SDG 16. | Investors should evaluate sovereign risk premiums; target logistics investments once reforms take hold. | Ministry of Finance, TRA, Planning Commission. |
| Senegal | Trade deficit severe, missing revenue/debt data. | Secure concessional financing while tightening import substitution programs; publish quarterly fiscal bulletin to close data gap. | SDG 10 (reduced inequality), SDG 16. | Businesses should anticipate policy to localise supply chains; plan for import licensing changes. | Ministry of Economy & Finance, BCEAO, APIX. |

### Implementation Checklist
- Validate flagged duplicates before building final visuals.
- Append qualitative context (commodity prices, subsidy reforms) to explain anomalies.
- Build dashboard views directly from `fiscal_stress_scorecard.csv` to ensure consistency across presentation assets.

