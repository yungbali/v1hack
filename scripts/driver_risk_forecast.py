"""
Generate analytical artifacts for the fiscal intelligence dashboard.

Outputs:
    - data/processed/fiscal_feature_matrix.csv
    - data/processed/fiscal_driver_analysis.csv
    - data/processed/fiscal_anomalies.csv
    - data/processed/fiscal_forecasts.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA

DATA_DIR = Path("data/processed")
OUTPUT_FEATURES = DATA_DIR / "fiscal_feature_matrix.csv"
OUTPUT_DRIVERS = DATA_DIR / "fiscal_driver_analysis.csv"
OUTPUT_ANOMALIES = DATA_DIR / "fiscal_anomalies.csv"
OUTPUT_FORECASTS = DATA_DIR / "fiscal_forecasts.csv"

FOCUS_COUNTRIES = ["Nigeria", "Ghana", "Kenya", "South Africa", "Egypt"]
FORECAST_HORIZON = 3


def load_clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "fiscal_data_clean.csv",
                     parse_dates=["Time", "Time_aligned"])
    df = df[~df["is_duplicate"]].copy()
    df["Year"] = df["Year"].astype(int)
    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    indicators = [
        "Budget Deficit/Surplus",
        "Revenue",
        "Tax Revenue",
        "Expenditure",
        "Capital Expenditure",
        "Nominal GDP",
        "Government Debt",
        "GDP Growth Rate",
    ]

    annual = (df[df["Indicator"].isin(indicators)].groupby(
        ["Country", "Year",
         "Indicator"])["Amount_standardised"].mean().unstack("Indicator"))

    annual = annual.sort_index().rename(
        columns={
            "Budget Deficit/Surplus": "deficit",
            "Revenue": "revenue",
            "Tax Revenue": "tax_revenue",
            "Expenditure": "expenditure",
            "Capital Expenditure": "capex",
            "Nominal GDP": "gdp_nominal",
            "Government Debt": "gov_debt",
            "GDP Growth Rate": "gdp_growth",
        })

    feature_df = annual.copy()
    feature_df[
        "deficit_pct_gdp"] = feature_df["deficit"] / feature_df["gdp_nominal"]
    feature_df[
        "revenue_pct_gdp"] = feature_df["revenue"] / feature_df["gdp_nominal"]
    feature_df[
        "tax_pct_gdp"] = feature_df["tax_revenue"] / feature_df["gdp_nominal"]
    feature_df[
        "debt_pct_gdp"] = feature_df["gov_debt"] / feature_df["gdp_nominal"]
    feature_df[
        "fiscal_burden"] = feature_df["gov_debt"] / feature_df["revenue"]

    recurrent = feature_df["expenditure"] - feature_df.get("capex").fillna(0)
    feature_df["wage_proxy_pct_gdp"] = recurrent / feature_df["gdp_nominal"]

    feature_df["revenue_volatility"] = (feature_df.groupby(
        level=0)["revenue_pct_gdp"].rolling(window=3,
                                            min_periods=2).std().droplevel(0))

    feature_df["structural_deficit"] = feature_df["deficit_pct_gdp"] - 0.3 * (
        feature_df["gdp_growth"] / 100.0)
    feature_df = feature_df.reset_index()
    feature_df = feature_df.dropna(subset=[
        "deficit_pct_gdp",
        "revenue_volatility",
        "wage_proxy_pct_gdp",
        "fiscal_burden",
        "gdp_growth",
        "debt_pct_gdp",
    ])
    feature_df.to_csv(OUTPUT_FEATURES, index=False)
    return feature_df


@dataclass
class RegressionResult:
    country: str
    coefficient: str
    beta: float
    p_value: float
    r_squared: float
    n_obs: int


def run_regressions(feature_df: pd.DataFrame) -> pd.DataFrame:
    results: List[RegressionResult] = []

    def _fit_model(subset: pd.DataFrame, country_label: str):
        y = subset["deficit_pct_gdp"]
        X = subset[[
            "revenue_volatility", "wage_proxy_pct_gdp", "fiscal_burden",
            "gdp_growth"
        ]]
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        for coef_name, beta in model.params.items():
            if coef_name == "const":
                continue
            results.append(
                RegressionResult(
                    country=country_label,
                    coefficient=coef_name,
                    beta=float(beta),
                    p_value=float(model.pvalues[coef_name]),
                    r_squared=float(model.rsquared),
                    n_obs=int(model.nobs),
                ))

    overall = feature_df.copy()
    overall["gdp_growth"] = overall["gdp_growth"] / 100.0
    required_cols = [
        "deficit_pct_gdp",
        "revenue_volatility",
        "wage_proxy_pct_gdp",
        "fiscal_burden",
        "gdp_growth",
    ]
    _fit_model(overall.dropna(subset=required_cols), "Pan-Africa")

    for country in FOCUS_COUNTRIES:
        subset = overall[overall["Country"] == country].dropna(
            subset=required_cols)
        if len(subset) >= 5:
            _fit_model(subset, country)

    driver_df = pd.DataFrame([r.__dict__ for r in results])
    driver_df["abs_beta"] = driver_df["beta"].abs()
    driver_df.sort_values(["country", "abs_beta"],
                          ascending=[True, False],
                          inplace=True)
    driver_df.drop(columns=["abs_beta"], inplace=True)
    driver_df.to_csv(OUTPUT_DRIVERS, index=False)
    return driver_df


def detect_anomalies(feature_df: pd.DataFrame) -> pd.DataFrame:
    anomalies = []
    for metric in ["debt_pct_gdp", "deficit_pct_gdp"]:
        grouped = feature_df.groupby("Country")
        for country, group in grouped:
            if group[metric].std(ddof=0) == 0 or len(group) < 3:
                continue
            zscores = (group[metric] -
                       group[metric].mean()) / group[metric].std(ddof=0)
            flags = zscores.abs() >= 2
            for (_, row), z, flag in zip(group.iterrows(), zscores, flags):
                if flag:
                    anomalies.append({
                        "Country": country,
                        "Year": int(row["Year"]),
                        "Metric": metric,
                        "Value": float(row[metric]),
                        "Zscore": float(z),
                    })
    anomalies_df = pd.DataFrame(anomalies)
    anomalies_df.to_csv(OUTPUT_ANOMALIES, index=False)
    return anomalies_df


def generate_forecasts(feature_df: pd.DataFrame) -> pd.DataFrame:
    forecasts = []
    for country in FOCUS_COUNTRIES:
        country_df = (feature_df[feature_df["Country"] == country].sort_values(
            "Year").set_index("Year"))
        for metric in ["deficit_pct_gdp", "debt_pct_gdp"]:
            series = country_df[metric].dropna()
            if len(series) < 6:
                continue
            try:
                model = ARIMA(series, order=(1, 1, 1)).fit()
                forecast = model.get_forecast(steps=FORECAST_HORIZON)
                mean = forecast.predicted_mean
                conf = forecast.conf_int()
                start_year = int(series.index.max()) + 1
                for step in range(FORECAST_HORIZON):
                    year = start_year + step
                    forecasts.append({
                        "Country": country,
                        "Metric": metric,
                        "Year": year,
                        "Forecast": float(mean.iloc[step]),
                        "Lower_CI": float(conf.iloc[step, 0]),
                        "Upper_CI": float(conf.iloc[step, 1]),
                    })
            except Exception as exc:  # pylint: disable=broad-except
                print(f"[WARN] Forecast failed for {country} {metric}: {exc}")
    forecast_df = pd.DataFrame(forecasts)
    forecast_df.to_csv(OUTPUT_FORECASTS, index=False)
    return forecast_df


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = load_clean_data()
    feature_df = build_feature_matrix(df)
    run_regressions(feature_df)
    detect_anomalies(feature_df)
    generate_forecasts(feature_df)
    print("✅ Driver, risk, and forecast artifacts generated.")


if __name__ == "__main__":
    main()
