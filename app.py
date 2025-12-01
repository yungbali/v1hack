"""
Fiscal Intelligence Dashboard for Policy Impact
Transforming Fiscal Data into Actionable Insights
"""

import json
import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.simulator import create_simulator_interface
from components.social_impact import (
    create_comparison_bar_chart,
    create_opportunity_cost_panel,
    identify_countries_debt_exceeds_health,
)
from components.data_governance import render_manual_review_interface
from components.ai_advisor import render_ai_advisor_interface
try:
    from components.pan_african import render_policy_relationship_map
except ImportError:  # fallback for older deployments

    def render_policy_relationship_map():
        st.warning(
            "Policy relationship map component is unavailable in this build.",
            icon="⚠️",
        )


from utils.constants import AFRICAN_COUNTRIES

warnings.filterwarnings("ignore")

DATA_DIR = Path("data/processed")
FOCUS_COUNTRIES = ["Nigeria", "Ghana", "Kenya", "South Africa", "Egypt"]
METRIC_LABEL_OVERRIDES = {
    "debt_pct_gdp": "Debt (% GDP)",
    "deficit_pct_gdp": "Deficit (% GDP)",
    "revenue_pct_gdp": "Revenue (% GDP)",
    "trade_balance_pct_gdp": "Trade Balance (% GDP)",
    "wage_proxy_pct_gdp": "Public Wage Bill (% GDP)",
    "revenue_volatility": "Revenue Volatility",
    "fiscal_burden": "Debt Service / Revenue",
    "gdp_growth": "GDP Growth (%)",
}


def clean_html(html: str) -> str:
    """Strip leading whitespace from HTML blocks to avoid Markdown fencing."""
    return "\n".join(line.strip() for line in html.splitlines())


# Page configuration
st.set_page_config(
    page_title="Fiscal Intelligence for Policy Impact",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

# Custom CSS
st.markdown(
    """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {
            --slate-50: #F8FAFB;
            --slate-100: #F1F5F9;
            --slate-200: #E2E8F0;
            --slate-300: #CBD5E1;
            --slate-400: #94A3B8;
            --slate-500: #64748B;
            --slate-600: #475569;
            --slate-900: #0F172A;
            --indigo-500: #667EEA;
            --indigo-600: #4F46E5;
            --amber-500: #F59E0B;
            --emerald-500: #10B981;
            --red-500: #EF4444;
        }

        .stApp,
        .stApp input,
        .stApp textarea,
        .stApp button {
            font-family: 'Inter', sans-serif;
            color: var(--slate-900);
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            letter-spacing: -0.025em;
        }

        .stApp {
            background-color: var(--slate-50);
        }

        footer { visibility: hidden; }
        .stDeployButton { display: none; }

        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid var(--slate-200);
        }

        .fi-page-header {
            margin-bottom: 2rem;
        }

        .fi-page-header h1 {
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .fi-page-header p {
            color: var(--slate-500);
            font-size: 0.95rem;
        }

        .fi-card {
            background: #FFFFFF;
        padding: 1.5rem;
            border-radius: 1rem;
            border: 1px solid var(--slate-200);
            box-shadow: 0 2px 4px -1px rgba(15, 23, 42, 0.08);
            transition: box-shadow 0.2s ease;
            height: 100%;
        }

        .fi-card:hover {
            box-shadow: 0 12px 24px -8px rgba(15, 23, 42, 0.2);
        }

        .fi-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .fi-card-body {
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .fi-label {
            font-size: 0.7rem;
        font-weight: 600;
            text-transform: uppercase;
            color: var(--slate-500);
            letter-spacing: 0.08em;
        }

        .fi-value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--slate-900);
        margin-right: 0.5rem;
        }

        .fi-context {
            font-size: 0.75rem;
            color: var(--slate-400);
            margin-top: 0.35rem;
        }

        .fi-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.65rem;
            border-radius: 0.6rem;
            font-size: 0.65rem;
            font-weight: 600;
            border: 1px solid transparent;
        }

        .fi-badge.critical {
        background: #FEF2F2;
            color: #B91C1C;
            border-color: #FECACA;
        }

        .fi-badge.warning {
            background: #FFFBEB;
            color: #B45309;
            border-color: #FDE68A;
        }

        .fi-badge.success {
        background: #ECFDF5;
            color: #047857;
            border-color: #A7F3D0;
        }

        .fi-badge.neutral {
            background: var(--slate-100);
            color: var(--slate-500);
            border-color: var(--slate-200);
        }

        .fi-delta {
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .fi-delta.up { color: var(--red-500); }
        .fi-delta.down { color: var(--emerald-500); }
        .fi-delta.neutral { color: var(--slate-500); }

        .fi-panel, .fi-insights, .fi-table-card {
            background: #FFFFFF;
            border-radius: 1rem;
            border: 1px solid var(--slate-200);
            box-shadow: 0 2px 4px -1px rgba(15, 23, 42, 0.06);
            height: 100%;
        }

        .fi-panel { padding: 1.5rem; }

        .fi-table-card {
            padding: 0;
            overflow: hidden;
        }

        .fi-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.5rem;
        }

        .fi-panel-heading {
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
        }

        .fi-panel-subtitle {
            font-size: 0.75rem;
            color: var(--slate-500);
            margin-top: 0.2rem;
        }

        .fi-insights { display: flex; flex-direction: column; }

        .fi-insights .fi-body {
            padding: 1.5rem;
            flex: 1;
            overflow-y: auto;
        }

        .fi-insights ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .space-y-4 > * + * { margin-top: 1rem; }

        .fi-insights footer {
            margin-top: auto;
            padding: 1rem 1.5rem;
            background: var(--slate-50);
            border-top: 1px solid var(--slate-200);
            border-bottom-left-radius: 1rem;
            border-bottom-right-radius: 1rem;
        }

        .fi-risk-badges {
            display: flex;
            gap: 1rem;
            overflow-x: auto;
        padding-bottom: 0.5rem;
        }

        .fi-risk-card {
            min-width: 210px;
            display: flex;
            gap: 0.75rem;
            align-items: center;
            padding: 0.85rem 1.1rem;
            border-radius: 0.9rem;
            border: 1px solid var(--slate-200);
            background: #FFFFFF;
            box-shadow: 0 2px 4px -1px rgba(15, 23, 42, 0.08);
        }

        .fi-risk-name {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--slate-900);
            margin: 0;
        }

        .fi-risk-meta {
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--slate-500);
            margin: 0;
        }

        .fi-risk-card.high {
            border-color: #FECACA;
            background: #FEF2F2;
        }

        .fi-risk-card.medium {
            border-color: #FDE68A;
            background: #FFFBEB;
        }

        .fi-risk-card.low {
            border-color: var(--slate-200);
        }

        .fi-risk-icon {
            height: 36px;
            width: 36px;
            border-radius: 0.65rem;
            display: grid;
            place-items: center;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .fi-risk-card.high .fi-risk-icon {
            background: #FEE2E2;
            color: #B91C1C;
        }

        .fi-risk-card.medium .fi-risk-icon {
            background: #FEF3C7;
            color: #B45309;
        }

        .fi-risk-card.low .fi-risk-icon {
            background: #E2E8F0;
            color: #475569;
        }

        .fi-table-wrapper { overflow-x: auto; }

        table.fi-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        table.fi-table thead { background: var(--slate-50); }

        table.fi-table th {
            padding: 0.85rem 1rem;
            text-align: left;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--slate-600);
            border-bottom: 1px solid var(--slate-200);
        }

        table.fi-table td {
            padding: 0.9rem 1rem;
            border-bottom: 1px solid var(--slate-100);
            color: var(--slate-900);
        }

        table.fi-table tbody tr:hover { background: rgba(226, 232, 240, 0.4); }

        .fi-status {
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }

        .fi-status.verified { color: #059669; }
        .fi-status.pending { color: #475569; }

        div[data-testid="stSlider"] > div:nth-child(1) {
            padding-bottom: 0;
        }

        div[data-testid="stSlider"] .css-14xtw13,
        div[data-testid="stSlider"] .stSlider > div > div > div:nth-child(2) {
            background: #FFFFFF;
            border: 2px solid #FFFFFF;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.2);
        }

        div[data-testid="stSlider"] .stSlider > div > div > div:nth-child(1) {
            background: var(--slate-200);
        }

        div[data-testid="stHorizontalBlock"] > div {
            gap: 1.25rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = 'All Countries'
if 'year_range' not in st.session_state:
    st.session_state.year_range = (2015, 2024)


# Load fiscal data
@st.cache_data
def load_fiscal_data():
    """Load all processed fiscal data and analytical artifacts."""

    def _safe_read_csv(filename: str, **kwargs) -> pd.DataFrame:
        path = DATA_DIR / filename
        if path.exists():
            return pd.read_csv(path, **kwargs)
        return pd.DataFrame()

    try:
        df = _safe_read_csv("fiscal_data_clean.csv",
                            parse_dates=["Time", "Time_aligned"])
        scorecard = _safe_read_csv("fiscal_stress_scorecard.csv")
        recommendations = _safe_read_csv("policy_recommendations.csv")
        feature_matrix = _safe_read_csv("fiscal_feature_matrix.csv")
        driver_df = _safe_read_csv("fiscal_driver_analysis.csv")
        anomalies_df = _safe_read_csv("fiscal_anomalies.csv")
        forecast_df = _safe_read_csv("fiscal_forecasts.csv")

        quality_report_path = DATA_DIR / "fiscal_data_quality_report.json"
        if quality_report_path.exists():
            with open(quality_report_path, "r", encoding="utf-8") as f:
                quality_report = json.load(f)
        else:
            quality_report = {}

        return (
            df,
            scorecard,
            recommendations,
            quality_report,
            feature_matrix,
            driver_df,
            anomalies_df,
            forecast_df,
        )
    except Exception as e:  # pylint: disable=broad-except
        st.error(f"❌ Error loading data: {e}")
        empty = pd.DataFrame()
        return empty, empty, empty, {}, empty, empty, empty, empty


@st.cache_data(ttl=600)
def load_dashboard_cache() -> pd.DataFrame:
    """Load cached dataset for simulator and social impact modules."""
    candidates = [
        Path("data/cached/dashboard_data.parquet"),
        Path("data/cached/test_cache.parquet"),
    ]
    cache_path = next((path for path in candidates if path.exists()), None)
    if cache_path is None:
        return pd.DataFrame()
    try:
        return pd.read_parquet(cache_path)
    except ImportError as exc:  # pragma: no cover - user environment
        st.warning(
            "⚠️ Install `pyarrow` or `fastparquet` to enable simulator and SDG datasets."
        )
        st.info(f"Underlying error: {exc}")
        return pd.DataFrame()
    except Exception as exc:  # pylint: disable=broad-except
        st.error(f"❌ Error loading cached dashboard data: {exc}")
        return pd.DataFrame()


def format_pct(value: float | None, decimals: int = 1) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "–"
    return f"{value * 100:.{decimals}f}%"


def latest_metrics(features: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    return (
        features.sort_values("Year").groupby("Country").tail(1).reset_index(
            drop=True))


def build_recommendation_cards(features: pd.DataFrame,
                               drivers: pd.DataFrame) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    latest = latest_metrics(features)
    if latest.empty or drivers.empty:
        return cards

    driver_templates = {
        "wage_proxy_pct_gdp": {
            "title":
            "Public wage bill is widening deficits",
            "action":
            "Freeze non-essential public hiring and digitise payroll to eliminate ghost workers; redirect savings into capital projects.",
            "target":
            lambda current:
            f"Reduce wage bill share from {format_pct(current)} to "
            f"{format_pct(max(current - 0.01, 0), 1)} by FY2027.",
            "timeline":
            "0–24 months",
        },
        "revenue_volatility": {
            "title": "Revenue base is too volatile",
            "action":
            "Automate VAT/e-invoicing for digital commerce and hedge commodity revenues to stabilise monthly inflows.",
            "target": lambda current:
            f"Cut revenue volatility to <{current * 10000:.0f} bps and lift revenue/GDP by +2pp within 18 months.",
            "timeline": "0–18 months",
        },
        "fiscal_burden": {
            "title": "Debt service is crowding out revenue",
            "action":
            "Reprofile short-term domestic debt into concessional instruments and run quarterly liability-management auctions.",
            "target": lambda current:
            f"Lower debt-service burden from {current:.1f}x to {max(current - 10, 30):.1f}x revenue by FY2026.",
            "timeline": "Immediate",
        },
        "gdp_growth": {
            "title": "Growth sensitivity drives deficits",
            "action":
            "Fast-track logistics and energy reforms to raise real GDP growth and stabilise tax buoyancy.",
            "target": lambda current:
            f"Maintain real GDP growth above {current:.1f}% through 2027 to cap deficits below 4% of GDP.",
            "timeline": "Structural (18+ months)",
        },
    }

    for country in drivers["country"].unique():
        if country == "Pan-Africa":
            continue
        country_driver = drivers[drivers["country"] == country].sort_values(
            "beta", key=lambda s: s.abs(), ascending=False)
        if country_driver.empty:
            continue
        best = country_driver.iloc[0]
        template = driver_templates.get(best["coefficient"])
        latest_row = latest[latest["Country"] == country]
        if template is None or latest_row.empty:
            continue

        current_metric = latest_row[best["coefficient"]].iloc[0]
        cards.append({
            "Country":
            country,
            "Narrative":
            template["title"],
            "Finding":
            (f"β = {best['beta']:.2f} with R² {best['r_squared']:.2f}. "
             "Every 1pp change in this driver shifts the deficit meaningfully."
             ),
            "Action":
            template["action"],
            "Target":
            template["target"](current_metric),
            "Timeline":
            template["timeline"],
        })
    return cards


def render_metric_card(title: str,
                       value: str,
                       subtitle: str,
                       *,
                       badge: str | None = None,
                       badge_variant: str = "neutral",
                       delta_text: str | None = None,
                       delta_direction: str = "neutral") -> str:
    """Return HTML snippet for a branded KPI card."""
    badge_html = f'<span class="fi-badge {badge_variant}">{badge}</span>' if badge else ""
    arrow = {"up": "▲", "down": "▼", "neutral": ""}.get(delta_direction, "")
    delta_html = (
        f'<span class="fi-delta {delta_direction}">{arrow} {delta_text}</span>'
        if delta_text else "")
    return clean_html(f"""
        <div class="fi-card">
            <div class="fi-card-top">
                <span class="fi-label">{title}</span>
                {badge_html}
            </div>
            <div class="fi-card-body">
                <span class="fi-value">{value}</span>
                {delta_html}
            </div>
            <p class="fi-context">{subtitle}</p>
        </div>
    """)


def prettify_metric(metric: str | None) -> str:
    if not metric:
        return ""
    return METRIC_LABEL_OVERRIDES.get(metric, metric.replace("_", " ").title())


def format_indicator_value(metric: str, value: float | None) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "–"
    metric_lower = metric.lower()
    if any(token in metric_lower
           for token in ("pct", "share", "rate", "ratio")):
        return f"{value * 100:.1f}%"
    return f"{value:,.2f}"


def severity_from_zscore(zscore: float | None) -> str:
    if zscore is None or (isinstance(zscore, float) and pd.isna(zscore)):
        return "Low"
    magnitude = abs(zscore)
    if magnitude >= 3:
        return "High"
    if magnitude >= 2:
        return "Medium"
    return "Low"


def render_risk_badges(anomalies_df: pd.DataFrame, max_cards: int = 4) -> str:
    if anomalies_df.empty:
        return ""
    summary = anomalies_df.copy()
    summary["Severity_bucket"] = summary["Zscore"].apply(severity_from_zscore)
    severity_order = {"Low": 0, "Medium": 1, "High": 2}

    def _max_severity(series: pd.Series) -> str:
        return max(series, key=lambda s: severity_order.get(s, 0))

    grouped = (summary.groupby("Country",
                               as_index=False).agg(alerts=("Country", "size"),
                                                   severity=("Severity_bucket",
                                                             _max_severity)))
    grouped["severity_score"] = grouped["severity"].map(severity_order).fillna(
        0)
    grouped = grouped.sort_values(["severity_score", "alerts"],
                                  ascending=[False, False]).head(max_cards)

    caption = {
        "High": "Critical Outliers",
        "Medium": "Warning Flags",
        "Low": "QA Check"
    }
    icon = {"High": "!", "Medium": "⚠️", "Low": "ℹ️"}

    cards = []
    for _, row in grouped.iterrows():
        sev = row["severity"]
        cards.append(
            clean_html(f"""
            <div class="fi-risk-card {sev.lower()}">
                <div class="fi-risk-icon">{icon.get(sev, 'ℹ️')}</div>
                <div>
                    <p class="fi-risk-name">{row['Country']}</p>
                    <p class="fi-risk-meta">{int(row['alerts'])} {caption.get(sev, 'alerts')}</p>
                </div>
            </div>
        """))
    return f'<div class="fi-risk-badges">{"".join(cards)}</div>'


def render_anomaly_table(anomalies_df: pd.DataFrame, max_rows: int = 6) -> str:
    if anomalies_df.empty:
        return "<p class='fi-context'>No anomaly alerts for the current selection.</p>"
    subset = anomalies_df.copy()
    subset["abs_z"] = subset["Zscore"].abs()
    subset = subset.sort_values("abs_z", ascending=False).head(max_rows)

    severity_badge = {
        "High": ("critical", "High"),
        "Medium": ("warning", "Medium"),
        "Low": ("neutral", "Low")
    }
    rows = []
    for _, row in subset.iterrows():
        sev = severity_from_zscore(row["Zscore"])
        badge_class, badge_label = severity_badge.get(sev, ("neutral", sev))
        status = "Review Pending" if sev != "Low" else "Verified"
        status_class = "pending" if sev != "Low" else "verified"
        metric_label = prettify_metric(str(row["Metric"]))
        value_display = format_indicator_value(str(row["Metric"]),
                                               row["Value"])
        rows.append(
            clean_html(f"""
            <tr>
                <td>{row['Country']}</td>
                <td>{metric_label}</td>
                <td><code>{value_display}</code></td>
                <td><span class="fi-badge {badge_class}">{badge_label}</span></td>
                <td><span class="fi-status {status_class}">{status}</span></td>
            </tr>
        """))

    return clean_html(f"""
        <div class="fi-table-wrapper">
            <table class="fi-table">
                <thead>
                    <tr>
                        <th>Country</th>
                        <th>Indicator</th>
                        <th>Recorded Value</th>
                        <th>Severity</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    """)


def filter_dashboard_cache(df: pd.DataFrame) -> pd.DataFrame:
    """Apply sidebar filters to cached dashboard data."""
    if df.empty:
        return df
    filtered = df.copy()
    if "year" in filtered.columns:
        start_year, end_year = st.session_state.year_range
        filtered = filtered[(filtered["year"] >= start_year)
                            & (filtered["year"] <= end_year)]

    selected_country = st.session_state.selected_country
    if selected_country != "All Countries":
        masks: list[pd.Series] = []
        if "country_name" in filtered.columns:
            masks.append(filtered["country_name"] == selected_country)
        if "country_code" in filtered.columns:
            code = next((cc for cc, name in AFRICAN_COUNTRIES.items()
                         if name == selected_country), None)
            if code:
                masks.append(filtered["country_code"] == code)
        if masks:
            combined = masks[0]
            for mask in masks[1:]:
                combined = combined | mask
            filtered = filtered[combined]
        else:
            filtered = filtered.iloc[0:0]
    return filtered


# Load data
with st.spinner('🔄 Loading fiscal intelligence data...'):
    (
        df,
        scorecard,
        recommendations,
        quality_report,
        feature_matrix,
        driver_df,
        anomalies_df,
        forecast_df,
    ) = load_fiscal_data()

dashboard_cache_df = load_dashboard_cache()

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0; border-bottom: 2px solid #E2E8F0;">
            <h1 style="font-size: 1.5rem; font-weight: 700; color: #0F172A; margin: 0;">
                📊 Fiscal Intelligence
            </h1>
            <p style="font-size: 0.875rem; color: #64748B; margin: 0.5rem 0 0 0;">
                Evidence-Based Policy Solutions
            </p>
        </div>
    """,
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    # api_key = st.text_input(
    #     "Gemini API Key",
    #     value=default_key,
    #     type="password",
    #     help="Provide a key to enable the AI Advisor",
    # )

    st.markdown("### 🎯 Navigate Dashboard")
    page = st.radio(
        "Select View",
        [
            "📊 Overview",
            "🗂 Presentation",
            "🤖 AI Advisor",
            "🧮 Driver Analysis",
            "⚠️ Risk & Forecast",
            "🧠 Simulator",
            "🌱 Social Impact",
            "📋 Recommendations",
            "🛠️ Data Governance",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    st.markdown("### 🔍 Filters")

    all_countries = ['All Countries'] + sorted(
        df['Country'].unique()) if not df.empty else ['All Countries']

    st.session_state.selected_country = st.selectbox("Select Country",
                                                     all_countries,
                                                     index=0)

    if not df.empty:
        min_year = int(df['Year'].min())
        max_year = int(df['Year'].max())
        st.session_state.year_range = st.slider("Year Range",
                                                min_value=min_year,
                                                max_value=max_year,
                                                value=(2015, max_year))

    st.markdown("<br>", unsafe_allow_html=True)

    # Data snapshot
    st.markdown("### 📈 Data Snapshot")
    if not df.empty:
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Countries", df['Country'].nunique())
        st.metric("Indicators", df['Indicator'].nunique())
        st.metric("Time Span",
                  f"{int(df['Year'].min())}–{int(df['Year'].max())}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk legend
    st.markdown("### 🚦 Risk Levels")
    st.markdown("""
        <div style="padding: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="width: 12px; height: 12px; background: #EF4444; border-radius: 50%;"></span>
                <span style="font-size: 0.875rem;">High Risk (>90% Debt/GDP)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="width: 12px; height: 12px; background: #F59E0B; border-radius: 50%;"></span>
                <span style="font-size: 0.875rem;">Moderate (60-90%)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 12px; height: 12px; background: #10B981; border-radius: 50%;"></span>
                <span style="font-size: 0.875rem;">Low Risk (<60%)</span>
        </div>
        </div>
    """,
                unsafe_allow_html=True)

# Filter data
filtered_df = df.copy() if not df.empty else df
if st.session_state.selected_country != 'All Countries':
    filtered_df = filtered_df[filtered_df['Country'] ==
                              st.session_state.selected_country]
if not filtered_df.empty:
    filtered_df = filtered_df[
        (filtered_df['Year'] >= st.session_state.year_range[0])
        & (filtered_df['Year'] <= st.session_state.year_range[1])]

# Main content
st.markdown(
    """
    <div style="padding: 0 0 2rem 0;">
        <h1 style="font-size: 3rem; font-weight: 800; color: #0F172A; margin: 0;">
            Fiscal Intelligence for Policy Impact
        </h1>
        <p style="font-size: 1.25rem; color: #64748B; margin: 0.5rem 0 0 0;">
            Evidence-Based Solutions for Sustainable Development Across Africa
            </p>
        </div>
""",
    unsafe_allow_html=True,
)

if page == "📊 Overview":
    st.markdown(
        clean_html("""
        <div class="fi-page-header">
            <h1>Executive Dashboard</h1>
            <p>Evidence-based solutions for sustainable development across Africa.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )

    if scorecard.empty:
        st.info(
            "Scorecard data is unavailable. Run the analytics pipeline to refresh artifacts."
        )
    else:
        total_countries = max(scorecard["Country"].nunique(), 1)
        debt_series = scorecard["Debt_to_GDP"].dropna()
        median_debt = debt_series.median(
        ) * 100 if not debt_series.empty else 0.0
        debt_delta = median_debt - 60
        debt_direction = "up" if debt_delta > 0 else "down" if debt_delta < 0 else "neutral"
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(
            render_metric_card(
                title="Median Debt-to-GDP",
                value=f"{median_debt:.1f}%",
                subtitle="Regional average vs. 60% target",
                badge="Critical" if median_debt > 60 else "On Track",
                badge_variant="critical" if median_debt > 60 else "success",
                delta_text=f"{debt_delta:+.1f} pts vs 60% target",
                delta_direction=debt_direction,
            ),
            unsafe_allow_html=True,
        )

        high_risk = int((scorecard["Debt_to_GDP"] > 0.9).sum())
        col2.markdown(
            render_metric_card(
                title="High Risk Nations",
                value=str(high_risk),
                subtitle="Debt > 90% of GDP",
                badge="Alert" if high_risk else "Stable",
                badge_variant="warning" if high_risk else "success",
                delta_text=f"{high_risk} of {total_countries} countries",
            ),
            unsafe_allow_html=True,
        )

        weak_revenue = int((scorecard["Revenue_to_GDP"] < 0.18).sum())
        weak_share = weak_revenue / total_countries if total_countries else 0
        col3.markdown(
            render_metric_card(
                title="Weak Revenue Base",
                value=str(weak_revenue),
                subtitle="Revenue < 18% of GDP",
                badge="Alert" if weak_revenue else "Healthy",
                badge_variant="warning" if weak_revenue else "success",
                delta_text=f"{weak_share:.0%} of cohort",
            ),
            unsafe_allow_html=True,
        )

        inflation_column = "Inflation Rate"
        if "Inflation Rate" not in scorecard.columns:
            inflation_column = ("Inflation_pct" if "Inflation_pct"
                                in scorecard.columns else None)
        avg_inflation = (scorecard[inflation_column].dropna().mean()
                         if inflation_column
                         and inflation_column in scorecard.columns else None)
        if avg_inflation is not None and not pd.isna(avg_inflation):
            inf_delta = avg_inflation - 10
            inf_direction = "up" if inf_delta > 0 else "down" if inf_delta < 0 else "neutral"
            col4.markdown(
                render_metric_card(
                    title="Average Inflation",
                    value=f"{avg_inflation:.1f}%",
                    subtitle="Year-over-year change",
                    badge="Elevated" if avg_inflation > 10 else "Stabilizing",
                    badge_variant="critical"
                    if avg_inflation > 10 else "success",
                    delta_text=f"{inf_delta:+.1f} pts vs 10% cap",
                    delta_direction=inf_direction,
                ),
                unsafe_allow_html=True,
            )
        else:
            col4.markdown(
                render_metric_card(
                    title="Average Inflation",
                    value="–",
                    subtitle="Year-over-year change",
                    badge="Data Gap",
                    badge_variant="neutral",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 1rem;'></div>",
                    unsafe_allow_html=True)

        chart_col, insight_col = st.columns((2, 1))
        focus_scorecard = scorecard[scorecard["Country"].isin(FOCUS_COUNTRIES)]
        if not focus_scorecard.empty:
            fig = go.Figure()
            palette = {
                "Nigeria": "#EF4444",
                "Egypt": "#3B82F6",
                "Ghana": "#10B981",
                "Kenya": "#F97316",
                "South Africa": "#8B5CF6",
            }
            for country in FOCUS_COUNTRIES:
                row = focus_scorecard[focus_scorecard["Country"] == country]
                if row.empty:
                    continue
                latest = row.iloc[0]
                rev = latest.get("Revenue_to_GDP")
                debt_val = latest.get("Debt_to_GDP")
                if pd.notna(rev) and pd.notna(debt_val):
                    fig.add_trace(
                        go.Scatter(
                            x=[rev * 100],
                            y=[debt_val * 100],
                            mode="markers+text",
                            name=country,
                            text=country,
                            textposition="top center",
                            marker=dict(
                                size=18,
                                color=palette.get(country, "#6366F1"),
                                line=dict(color="white", width=2),
                            ),
                            hovertemplate=
                            "<b>%{text}</b><br>Revenue/GDP: %{x:.1f}%<br>Debt/GDP: %{y:.1f}%<extra></extra>",
                        ))
            fig.add_hline(
                y=90,
                line_dash="dash",
                line_color="#EF4444",
                annotation_text="90% Threshold",
            )
            fig.add_vline(
                x=20,
                line_dash="dash",
                line_color="#10B981",
                annotation_text="20% Target",
            )
            fig.update_layout(
                xaxis_title="Revenue to GDP (%)",
                yaxis_title="Debt to GDP (%)",
                height=420,
                showlegend=False,
                hovermode="closest",
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=16, t=16, b=40),
            )
            chart_col.markdown(
                """
                <div class="fi-panel">
                    <div class="fi-panel-header">
                        <div>
                            <h3 class="fi-panel-heading">Debt Burden vs. Revenue Mobilisation</h3>
                            <p class="fi-panel-subtitle">Correlation of fiscal buffers across focus economies</p>
                        </div>
                        <div style="display:flex; gap:0.75rem; font-size:0.7rem; text-transform:uppercase; color: var(--slate-500);">
                            <span>● High Risk</span>
                            <span>● Sustainable</span>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            chart_col.plotly_chart(fig,
                                   width="stretch",
                                   config={"displayModeBar": False})
            chart_col.markdown("</div>", unsafe_allow_html=True)
        else:
            chart_col.info("Insufficient data to render the risk radar.")

        insight_col.markdown(
            clean_html("""
            <div class="fi-insights">
                <div class="fi-panel-header" style="padding: 1.5rem 1.5rem 0 1.5rem;">
                    <div>
                        <h3 class="fi-panel-heading">Key Insights</h3>
                        <p class="fi-panel-subtitle">Automated from fiscal_stress_scorecard</p>
                    </div>
                </div>
                <div class="fi-body">
                    <ul class="space-y-4" style="display:flex; flex-direction:column; gap:1rem;">
                        <li>
                            <div class="fi-risk-name" style="font-size:0.9rem;">Egypt Debt Exposure</div>
                            <p class="fi-risk-meta">Remains above the 90% danger zone and requires near-term consolidation.</p>
                        </li>
                        <li>
                            <div class="fi-risk-name" style="font-size:0.9rem;">Revenue Shortfall</div>
                            <p class="fi-risk-meta">Nigeria and Ghana collect below 20% of GDP, constraining buffers.</p>
                        </li>
                        <li>
                            <div class="fi-risk-name" style="font-size:0.9rem;">Volatility Driver</div>
                            <p class="fi-risk-meta">Revenue volatility is the dominant deficit driver in resource economies.</p>
                        </li>
                    </ul>
                </div>
                <footer>
                    <button style="width:100%; border:1px solid var(--indigo-500); color: var(--indigo-500); background: transparent; border-radius:0.6rem; padding:0.6rem 1rem; font-size:0.75rem; font-weight:600;">View Full Report</button>
                </footer>
            </div>
            """),
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 1.5rem;'></div>",
                    unsafe_allow_html=True)

        ts_col, driver_col = st.columns(2)
        ts_col.markdown(
            clean_html("""
            <div class="fi-panel">
                <div class="fi-panel-header">
                    <div>
                        <h3 class="fi-panel-heading">Historical Trends</h3>
                        <p class="fi-panel-subtitle">Track fiscal signals for the selected universe</p>
                    </div>
                </div>
            """),
            unsafe_allow_html=True,
        )
        trend_choice = ts_col.radio(
            "Historical Trend",
            ["Revenue", "Debt", "Inflation"],
            horizontal=True,
            label_visibility="collapsed",
            key="trend_toggle",
        )
        trend_map = {
            "Revenue":
            ("Revenue", "Amount_standardised", "Revenue (Billions)"),
            "Debt":
            ("Government Debt", "Amount_standardised", "Debt (Billions)"),
            "Inflation":
            ("Inflation Rate", "Amount_numeric", "Inflation Rate (%)"),
        }
        indicator, value_field, label = trend_map[trend_choice]
        trend_df = filtered_df[filtered_df["Indicator"] == indicator]
        if not trend_df.empty:
            trend_fig = px.line(
                trend_df.sort_values("Year"),
                x="Year",
                y=value_field,
                color="Country",
                labels={value_field: label},
            )
            if indicator == "Inflation Rate":
                trend_fig.add_hline(
                    y=10,
                    line_dash="dash",
                    line_color="#EF4444",
                    annotation_text="10% cap",
                )
            trend_fig.update_layout(
                height=320,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            ts_col.plotly_chart(
                trend_fig,
                width="stretch",
                config={"displayModeBar": False},
            )
        else:
            ts_col.info(
                "No data available for the selected trend and filters.")
        ts_col.markdown("</div>", unsafe_allow_html=True)

        driver_col.markdown(
            clean_html("""
            <div class="fi-panel">
                <div class="fi-panel-header">
                    <div>
                        <h3 class="fi-panel-heading">Deficit Drivers (MLR)</h3>
                        <p class="fi-panel-subtitle">Top coefficients for current selection</p>
                    </div>
                </div>
            """),
            unsafe_allow_html=True,
        )
        if driver_df.empty:
            driver_col.info(
                "Run `python scripts/driver_risk_forecast.py` to generate regression outputs."
            )
        else:
            available_countries = [
                c for c in driver_df["country"].unique() if c != "Pan-Africa"
            ]
            driver_country = st.session_state.selected_country
            if (driver_country == "All Countries"
                    or driver_country not in available_countries):
                driver_country = available_countries[
                    0] if available_countries else None
            if driver_country:
                subset = driver_df[driver_df["country"] ==
                                   driver_country].sort_values(
                                       "beta",
                                       key=lambda s: s.abs(),
                                       ascending=False)
                if subset.empty:
                    driver_col.info(
                        f"No regression results for {driver_country}.")
                else:
                    r_squared = subset["r_squared"].iloc[0]
                    driver_col.markdown(
                        f"<p class='fi-context' style='margin-bottom:0.5rem;'>Model R²: {r_squared:.2f} • Country: {driver_country}</p>",
                        unsafe_allow_html=True,
                    )
                    colors = [
                        "#EF4444" if beta > 0 else "#10B981"
                        for beta in subset["beta"]
                    ]
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(
                            x=subset["beta"],
                            y=subset["coefficient"],
                            orientation="h",
                            marker=dict(
                                color=colors,
                                line=dict(color="rgba(15,23,42,0.1)", width=1),
                            ),
                        ))
                    fig.update_layout(
                        height=320,
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis_title="Impact coefficient (β)",
                        yaxis_title="Driver",
                        plot_bgcolor="#FFFFFF",
                        paper_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                    )
                    driver_col.plotly_chart(
                        fig,
                        width="stretch",
                        config={"displayModeBar": False},
                    )
            else:
                driver_col.info("No driver analytics available.")
        driver_col.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>",
                    unsafe_allow_html=True)

        st.markdown(
            clean_html("""
            <div class="fi-panel-header" style="padding-left:0;">
                <div>
                    <h3 class="fi-panel-heading">Risk Monitoring & Anomalies</h3>
                    <p class="fi-panel-subtitle">Source: fiscal_anomalies.csv</p>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        badges_html = render_risk_badges(anomalies_df)
        if badges_html:
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.info("No anomalies found for the current filters.")

        table_html = render_anomaly_table(anomalies_df, max_rows=6)
        st.markdown(
            clean_html(f"""
            <div class="fi-table-card" style="margin-top:1rem;">
                {table_html}
                <div style="padding:0.85rem 1rem; border-top:1px solid var(--slate-200); background: var(--slate-50); text-align:right;">
                    <span class="fi-status pending">View all anomalies →</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

elif page == "🗂 Presentation":
    st.markdown(
        clean_html("""
        <div class="fi-page-header">
            <h1>The Fiscal Narrative</h1>
            <p>Connecting data points to the human story of economic resilience.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )
    if scorecard.empty:
        st.info("Load the core datasets to populate the presentation view.")
    else:
        high_debt = int((scorecard["Debt_to_GDP"] > 0.9).sum())
        weak_rev = int((scorecard["Revenue_to_GDP"] < 0.18).sum())
        inflation_col = ("Inflation Rate" if "Inflation Rate"
                         in scorecard.columns else "Inflation_pct")
        avg_inf = (scorecard[inflation_col].dropna().mean() if inflation_col
                   and inflation_col in scorecard.columns else 0)
        anomaly_count = len(anomalies_df) if not anomalies_df.empty else 0
        forecast_countries = (forecast_df["Country"].nunique()
                              if not forecast_df.empty else 0)

        social_alerts = 0
        if not dashboard_cache_df.empty:
            social_slice = filter_dashboard_cache(dashboard_cache_df)
            required_cols = {
                "year",
                "country_name",
                "debt_service_usd",
                "gdp_usd",
                "health_pct_gdp",
            }
            if not social_slice.empty and required_cols.issubset(
                    social_slice.columns):
                latest_year = int(social_slice["year"].max())
                social_alerts = len(
                    identify_countries_debt_exceeds_health(social_slice,
                                                           year=latest_year))

        st.markdown(
            clean_html(f"""
            <div style="margin-bottom: 2rem; padding: 1.5rem; background: white; border-radius: 0.75rem; border-left: 4px solid #4F46E5; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <h3 style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin-bottom: 0.75rem;">Executive Snapshot: The "So What?"</h3>
                <p style="font-size: 1rem; line-height: 1.6; color: #334155;">
                    Here is the headline: We have <strong>{high_debt} countries</strong> standing on the precipice of a 90% debt-to-GDP cliff.
                    Meanwhile, <strong>{weak_rev} economies</strong> are collecting less than 18 cents on the dollar in revenue.
                </p>
                <p style="font-size: 1rem; line-height: 1.6; color: #334155; margin-top: 1rem;">
                    Inflation is averaging <strong>{avg_inf:.1f}%</strong>—high, yes, but stabilizing in key markets.
                    The opportunity isn't just in restructuring debt; it is in <em>reclaiming fiscal space</em>.
                </p>
            </div>
            """),
            unsafe_allow_html=True,
        )

        st.markdown(
            clean_html("""
            <div class="section-header" style="margin-top:3rem; margin-bottom:1rem;">
                <h3>🔍 How We Know What We Know: The Insight Engine</h3>
            </div>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem;">
                <div style="flex: 1; min-width: 200px; padding: 1rem; background: #F1F5F9; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <strong style="color: #4F46E5;">1. Raw Data Ingestion</strong><br>
                    <span style="font-size: 0.85rem; color: #64748B;">CSV/Excel pipelines scrape and structure disparate fiscal reports.</span>
                </div>
                <div style="display:flex; align-items:center; color:#94A3B8;">➝</div>
                <div style="flex: 1; min-width: 200px; padding: 1rem; background: #F1F5F9; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <strong style="color: #0891B2;">2. Anomaly Detection</strong><br>
                    <span style="font-size: 0.85rem; color: #64748B;">Z-score algorithms flag outliers (e.g., sudden debt spikes) for review.</span>
                </div>
                <div style="display:flex; align-items:center; color:#94A3B8;">➝</div>
                <div style="flex: 1; min-width: 200px; padding: 1rem; background: #F1F5F9; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <strong style="color: #D97706;">3. Driver Analysis (MLR)</strong><br>
                    <span style="font-size: 0.85rem; color: #64748B;">Regressions isolate variables (wage bill, volatility) driving deficits.</span>
                </div>
                <div style="display:flex; align-items:center; color:#94A3B8;">➝</div>
                <div style="flex: 1; min-width: 200px; padding: 1rem; background: #F1F5F9; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <strong style="color: #16A34A;">4. Strategic Output</strong><br>
                    <span style="font-size: 0.85rem; color: #64748B;">Simulators & scorecards guide specific policy interventions.</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        st.markdown(
            clean_html("""
            <div class="section-header" style="margin-top:3rem;">
                <h3>🤖 Future State: AI-Augmented Fiscal Intelligence</h3>
            </div>
            <p style="color:#64748B; margin-bottom: 1.5rem;">Moving from descriptive analytics to predictive, AI-driven oversight.</p>
            """),
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                clean_html("""
                <div class="fi-card">
                    <div class="fi-card-top">
                        <span class="fi-label">Phase 1: Real-Time Processing</span>
                        <span class="fi-badge warning">Next Step</span>
                    </div>
                    <p style="font-weight: 600; margin-top: 0.5rem;">Automated Data Ingestion & Cleaning</p>
                    <p class="fi-context">Deploy LLM agents to parse unstructured PDF budget reports and scrape ministry portals daily, reducing lag from months to hours.</p>
                </div>
                """),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                clean_html("""
                <div class="fi-card">
                    <div class="fi-card-top">
                        <span class="fi-label">Phase 2: Predictive Governance</span>
                        <span class="fi-badge neutral">Planned</span>
                    </div>
                    <p style="font-weight: 600; margin-top: 0.5rem;">Scenario-Based AI Simulations</p>
                    <p class="fi-context">Integrate generative models to simulate complex shocks (commodity crashes, pandemics) and recommend preemptive fiscal buffers.</p>
                </div>
                """),
                unsafe_allow_html=True,
            )

        st.markdown(
            clean_html("""
            <div class="section-header" style="margin-top:3rem;">
                <h3>🛠️ Implementation: Manual Review Workflow</h3>
            </div>
            <div style="background: white; border-radius: 0.75rem; border: 1px solid #E2E8F0; padding: 1.5rem;">
                <p style="font-size: 0.95rem; color: #334155; margin-bottom: 1rem;">
                    Technology flags the anomaly; humans validate the context. Our implementation plan for the "Manual Review" queue ensures high data integrity without bottlenecks.
                </p>
                <ul style="list-style: none; padding: 0; color: #475569; font-size: 0.9rem; line-height: 1.8;">
                    <li style="display: flex; gap: 0.75rem; align-items: start; margin-bottom: 0.5rem;">
                        <span style="background: #EEF2FF; color: #4F46E5; padding: 0.1rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">STEP 1</span>
                        <span><strong>AI Pre-Screening:</strong> Deduplication algorithms cluster similar records (e.g., "Min. of Finance" vs "MoF") and assign confidence scores.</span>
                    </li>
                    <li style="display: flex; gap: 0.75rem; align-items: start; margin-bottom: 0.5rem;">
                        <span style="background: #EEF2FF; color: #4F46E5; padding: 0.1rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">STEP 2</span>
                        <span><strong>Analyst Queue:</strong> Low-confidence matches move to the Data Governance tab for analyst decisioning.</span>
                    </li>
                    <li style="display: flex; gap: 0.75rem; align-items: start;">
                        <span style="background: #EEF2FF; color: #4F46E5; padding: 0.1rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">STEP 3</span>
                        <span><strong>Feedback Loop:</strong> Analyst decisions retrain the matching model, improving auto-resolution rates over time.</span>
                    </li>
                </ul>
            </div>
            """),
            unsafe_allow_html=True,
        )

        evidence_map = [
            (
                "Stress Scorecard",
                "Threshold benchmarking across 5 ratios.",
                f"{high_debt} high-debt countries identified.",
                "Stage debt reprofiling playbooks; feed Recommendations tab.",
            ),
            (
                "Driver Regression",
                "Country-level MLR on deficit drivers.",
                "Top driver surfaced per country to match reforms.",
                "Align policy levers (wage bill, volatility, burden) with findings.",
            ),
            (
                "Anomaly Scanner",
                "Z-score + QA pipeline on fiscal flows.",
                f"{anomaly_count} anomalies flagged for review."
                if anomaly_count else "No anomalies currently raised.",
                "Escalate to due-diligence log; update QA tab.",
            ),
            (
                "Forecast Engine",
                "ARIMA fan charts on deficit/debt trajectories.",
                f"{forecast_countries} countries with 3-year outlook.",
                "Inform simulator scenarios & cash-buffer planning.",
            ),
            (
                "Social Impact Lab",
                "Debt vs. health/education comparison + opportunity cost.",
                f"{social_alerts} countries where debt crowds out health."
                if social_alerts else "Awaiting latest SDG feed.",
                "Use findings in SDG discussion notes & partner briefings.",
            ),
        ]

        rows_html = "".join(f"""
            <tr>
                <td><strong>{row[0]}</strong></td>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
                <td>{row[3]}</td>
            </tr>
            """ for row in evidence_map)
        st.markdown(
            clean_html(f"""
            <div class="fi-table-wrapper" style="margin-top:1rem;">
                <table class="fi-table">
                    <thead>
                        <tr>
                            <th>Data Source</th>
                            <th>Method</th>
                            <th>Insight</th>
                            <th>Policy Response</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """),
            unsafe_allow_html=True,
        )

elif page == "🤖 AI Advisor":
    render_ai_advisor_interface(df, api_key)

elif page == "🧮 Driver Analysis":
    st.markdown(
        '<div class="section-header">🧮 Deficit Driver Analysis (MLR)</div>',
        unsafe_allow_html=True)
    if driver_df.empty:
        st.warning(
            "Run `python scripts/driver_risk_forecast.py` to generate regression outputs."
        )
    else:
        available_countries = [
            c for c in driver_df["country"].unique() if c != "Pan-Africa"
        ]
        if not available_countries:
            available_countries = driver_df["country"].unique().tolist()
        selected = st.selectbox("Select country", available_countries, index=0)
        subset = driver_df[driver_df["country"] == selected]
        if subset.empty:
            st.info("No regression results for the selected country.")
        else:
            st.metric("Model R²", f"{subset['r_squared'].iloc[0]:.2f}")
            fig = px.bar(
                subset,
                x="coefficient",
                y="beta",
                color="beta",
                title=f"Impact Coefficients for {selected}",
                color_continuous_scale="RdBu",
            )
            fig.update_layout(yaxis_title="β coefficient",
                              xaxis_title="Driver",
                              coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
            st.dataframe(subset[[
                "coefficient", "beta", "p_value", "r_squared", "n_obs"
            ]],
                         width="stretch")
            top_driver = subset.iloc[0]
            st.markdown(f"""
                **Interpretation:** Every 1pp increase in `{top_driver['coefficient']}` shifts the deficit by
                **{top_driver['beta']:.2f}pp of GDP** (p-value {top_driver['p_value']:.3f}).
                Focus reforms on this lever to bend the deficit path.
                """)

elif page == "⚠️ Risk & Forecast":
    st.markdown('<div class="section-header">⚠️ Risk & Forecast View</div>',
                unsafe_allow_html=True)

    if anomalies_df.empty:
        st.info(
            "No anomaly flags yet. Regenerate analytics to populate this view."
        )
    else:
        top_risks = anomalies_df["Country"].value_counts().head(4)
        cols = st.columns(len(top_risks))
        for col, (country, count) in zip(cols, top_risks.items(),
                                         strict=False):
            col.metric(country, f"{count} critical outliers")
        st.dataframe(anomalies_df, width="stretch")

    st.markdown("### 📦 Distribution Stress Test")
    if feature_matrix.empty:
        st.info("Feature matrix missing; rerun analysis script.")
    else:
        metric_options = {
            "Debt-to-GDP (%)": "debt_pct_gdp",
            "Deficit-to-GDP (%)": "deficit_pct_gdp",
        }
        metric_label = st.selectbox("Select metric",
                                    list(metric_options.keys()))
        metric_col = metric_options[metric_label]
        box_df = feature_matrix[["Country", "Year", metric_col]].dropna()
        box_df["value_pct"] = box_df[metric_col] * 100
        fig = px.box(
            box_df,
            x="Country",
            y="value_pct",
            points="suspectedoutliers",
            title=f"{metric_label} distribution (2000–2024)",
            labels={"value_pct": metric_label},
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("### 🔮 Forecasting (ARIMA)")
    if forecast_df.empty or feature_matrix.empty:
        st.info("Forecast outputs unavailable.")
    else:
        countries = sorted(forecast_df["Country"].unique())
        forecast_country = st.selectbox("Country",
                                        countries,
                                        key="forecast_country")
        metric_choice = st.radio("Metric", ["deficit_pct_gdp", "debt_pct_gdp"],
                                 format_func=lambda x: "Deficit (% GDP)"
                                 if x == "deficit_pct_gdp" else "Debt (% GDP)")
        hist = (feature_matrix[feature_matrix["Country"] ==
                               forecast_country].sort_values("Year")[[
                                   "Year", metric_choice
                               ]].dropna())
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist["Year"],
                y=hist[metric_choice] * 100,
                mode="lines+markers",
                name="Historical",
                line=dict(color="#2563EB"),
            ))
        fc_subset = forecast_df[(forecast_df["Country"] == forecast_country)
                                & (forecast_df["Metric"] == metric_choice)]
        if not fc_subset.empty:
            fig.add_trace(
                go.Scatter(
                    x=fc_subset["Year"],
                    y=fc_subset["Forecast"] * 100,
                    mode="lines+markers",
                    name="Forecast",
                    line=dict(color="#DC2626", dash="dash"),
                ))
            fig.add_trace(
                go.Scatter(
                    x=fc_subset["Year"],
                    y=fc_subset["Upper_CI"] * 100,
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                ))
            fig.add_trace(
                go.Scatter(
                    x=fc_subset["Year"],
                    y=fc_subset["Lower_CI"] * 100,
                    mode="lines",
                    fill="tonexty",
                    line=dict(width=0),
                    fillcolor="rgba(220,38,38,0.2)",
                    name="95% CI",
                ))
        fig.update_layout(
            title=
            f"{forecast_country}: {metric_choice.replace('_', ' ').title()} outlook",
            yaxis_title="Percent of GDP",
        )
        st.plotly_chart(fig, width="stretch")

elif page == "🧠 Simulator":
    st.markdown(
        clean_html("""
        <div class="fi-page-header">
            <h1>Predictive Simulator</h1>
            <p>Model restructuring levers and quantify the fiscal space you can unlock.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )
    if dashboard_cache_df.empty:
        st.warning(
            "Simulator dataset unavailable. Refresh `data/cached/dashboard_data.parquet` and install `pyarrow`."
        )
    else:
        simulator_df = filter_dashboard_cache(dashboard_cache_df)
        if simulator_df.empty:
            st.info("No country data matches the current filters.")
        else:
            default_code = next(
                (code for code, name in AFRICAN_COUNTRIES.items()
                 if name == st.session_state.selected_country),
                "NGA",
            )
            create_simulator_interface(simulator_df,
                                       default_country=default_code)

elif page == "🌱 Social Impact":
    st.markdown(
        clean_html("""
        <div class="fi-page-header">
            <h1>SDG & Social Impact</h1>
            <p>Contrast debt service with essential social spending to spotlight trade-offs.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )
    if dashboard_cache_df.empty:
        st.warning(
            "Social impact dataset unavailable. Refresh `data/cached/dashboard_data.parquet`."
        )
    else:
        social_df = filter_dashboard_cache(dashboard_cache_df)
        required_cols = {
            "year",
            "country_name",
            "debt_service_usd",
            "gdp_usd",
            "health_pct_gdp",
            "education_pct_gdp",
        }
        missing = sorted(required_cols - set(social_df.columns))
        if social_df.empty:
            st.info("No social spending data found for the current filters.")
        elif missing:
            st.warning(
                f"Social impact view missing columns: {', '.join(missing)}. Rebuild the cached dataset."
            )
        else:
            latest_year = int(social_df["year"].max())
            latest_slice = social_df[social_df["year"] == latest_year]
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            median_health = latest_slice["health_pct_gdp"].median()
            median_education = latest_slice["education_pct_gdp"].median()
            median_debt_service = latest_slice["debt_service_usd"].median()
            combined_social = (latest_slice["health_pct_gdp"] +
                               latest_slice["education_pct_gdp"]).median()

            kpi_col1.markdown(
                clean_html(f"""
                <div class="fi-card">
                    <div class="fi-card-top">
                        <span class="fi-label">Median Health Spend</span>
                    </div>
                    <div class="fi-card-body">
                        <span class="fi-value">{median_health:.1f}%</span>
                    </div>
                    <p class="fi-context">Share of GDP ({latest_year})</p>
                </div>
                """),
                unsafe_allow_html=True,
            )
            kpi_col2.markdown(
                clean_html(f"""
                <div class="fi-card">
                    <div class="fi-card-top">
                        <span class="fi-label">Median Education Spend</span>
                    </div>
                    <div class="fi-card-body">
                        <span class="fi-value">{median_education:.1f}%</span>
                    </div>
                    <p class="fi-context">Share of GDP ({latest_year})</p>
                </div>
                """),
                unsafe_allow_html=True,
            )
            countries_over_health = identify_countries_debt_exceeds_health(
                social_df, year=latest_year)
            kpi_col3.markdown(
                clean_html(f"""
                <div class="fi-card">
                    <div class="fi-card-top">
                        <span class="fi-label">Debt > Health Spend</span>
                        <span class="fi-badge critical">Alert</span>
                    </div>
                    <div class="fi-card-body">
                        <span class="fi-value">{len(countries_over_health)}</span>
                    </div>
                    <p class="fi-context">Countries in {latest_year}</p>
                </div>
                """),
                unsafe_allow_html=True,
            )
            kpi_col4.markdown(
                clean_html(f"""
                <div class="fi-card">
                    <div class="fi-card-top">
                        <span class="fi-label">Combined Social Spend</span>
                    </div>
                    <div class="fi-card-body">
                        <span class="fi-value">{combined_social:.1f}%</span>
                    </div>
                    <p class="fi-context">Median of health + education</p>
                </div>
                """),
                unsafe_allow_html=True,
            )

            st.markdown("<div style='margin-top:1.5rem;'></div>",
                        unsafe_allow_html=True)
            chart = create_comparison_bar_chart(social_df, year=latest_year)
            st.plotly_chart(chart, width="stretch")

            if countries_over_health:
                preview = ", ".join(countries_over_health[:8])
                suffix = "…" if len(countries_over_health) > 8 else ""
                st.markdown(
                    clean_html(f"""
                    <div style="margin-top: 1rem; padding: 1rem; border-radius: 0.75rem; border: 1px solid #FEE2E2; background:#FEF2F2;">
                        <p style="font-size:0.85rem; color:#7F1D1D; margin:0;">
                            ⚠️ <strong>{len(countries_over_health)} countries</strong> spend more on debt service than health:
                            {preview}{suffix}
                        </p>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            if pd.notna(median_debt_service) and median_debt_service > 0:
                opportunity = create_opportunity_cost_panel(
                    "Median Basket", median_debt_service)
                st.markdown(
                    clean_html("""
                    <div style="margin:2rem 0 1rem 0;">
                        <h3 style="font-size:1.2rem; font-weight:600; color:#0F172A; margin-bottom:0.35rem;">
                            What current debt service could fund
                        </h3>
                        <p style="font-size:0.85rem; color:#64748B;">
                            Translating the median annual debt payment into SDG-aligned investments.
                        </p>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
                opp_cols = st.columns(4)
                for col, key in zip(
                        opp_cols,
                    ["schools", "hospitals", "vaccine_doses", "teachers"],
                        strict=False,
                ):
                    card = opportunity[key]
                    col.markdown(
                        clean_html(f"""
                        <div style="border-radius:0.9rem; border:1px solid #E2E8F0; padding:1.25rem; background:white; text-align:center;">
                            <div style="height:3rem; width:3rem; margin:0 auto 1rem auto; border-radius:0.75rem; background:#F8FAFC; display:flex; align-items:center; justify-content:center;">
                                <span style="font-size:1.5rem;">{card['emoji']}</span>
                            </div>
                            <p style="font-size:2rem; font-weight:600; margin:0;">{card['quantity']:,}</p>
                            <p style="font-size:0.9rem; color:#475569; margin:0.25rem 0;">{card['label']}</p>
                            <p style="font-size:0.75rem; color:#94A3B8; margin:0;">@ ${card['unit_cost']:,.0f} each</p>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )

elif page == "📋 Recommendations":
    st.markdown(
        '<div class="section-header">📋 Actionable Recommendations</div>',
        unsafe_allow_html=True)

    # Add Insight-to-Action Map (New Feature)
    with st.expander("🗺️ View Policy Relationship Map", expanded=False):
        st.markdown("""
        <p style="font-size:0.9rem; color:#64748B; margin-bottom:1rem;">
            This map visualizes how specific fiscal signals (like high wage bills or volatility)
            logically flow into the recommended policy interventions below.
        </p>
        """,
                    unsafe_allow_html=True)
        render_policy_relationship_map()

    cards = build_recommendation_cards(feature_matrix, driver_df)
    if not cards:
        st.info("Generate analytics to power recommendation engine.")
    else:
        for card in cards:
            with st.expander(f"🌍 {card['Country']}", expanded=True):
                st.markdown(f"**Finding:** {card['Finding']}")
                st.markdown(f"**Action:** {card['Action']}")
                st.markdown(f"**Target:** {card['Target']}")
                st.markdown(f"**Timeline:** {card['Timeline']}")

elif page == "🛠️ Data Governance":
    st.markdown('<div class="section-header">🛠️ Data Governance & QA</div>',
                unsafe_allow_html=True)
    tab1, tab2 = st.tabs(
        ["🔍 Manual Review Queue", "📑 Quality Report & Limitations"])
    with tab1:
        render_manual_review_interface()
    with tab2:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total Records",
                f"{quality_report.get('total_records', len(df)):,}",
            )
        with col2:
            st.metric(
                "Countries",
                df['Country'].nunique() if not df.empty else 0,
            )
        with col3:
            st.metric(
                "Duplicates Resolved",
                quality_report.get("duplicates_resolved", 0),
            )
        with col4:
            st.metric(
                "Manual Review Pending",
                quality_report.get("duplicates_manual_review", 0),
            )
        st.markdown("""
        ### Known Data Limitations
        - **Missing wage-bill microdata:** We proxy the public wage bill using recurrent expenditure, which may understate payroll leakages.
        - **Commodity exposure:** No linkage to oil/mineral price indices, so revenue volatility ignores global price shocks.
        - **Informal economy:** Tax capacity excludes informal sector potential, biasing revenue-to-GDP targets downward.
        - **Debt composition:** Lack of creditor/maturity breakdown prevents modelling restructuring tactics by instrument.

        ### Future Enhancements
        - Integrate climate and commodity stress scenarios to test revenue shocks.
        - Add micro-level tax compliance data (POS, mobile money) to refine digital VAT recommendations.
        - Capture debt maturity and currency mix to simulate liability-management savings.
        """)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 0.75rem; text-align: center; color: white;">
        <h3 style="font-size: 1.75rem; font-weight: 700; margin: 0 0 1rem 0;">
            📊 Fiscal Intelligence Platform
        </h3>
        <p style="font-size: 1.125rem; margin: 0;">
            Transforming Fiscal Data into Sustainable Development Solutions
        </p>
        </div>
""",
            unsafe_allow_html=True)
