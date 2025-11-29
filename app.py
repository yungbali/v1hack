"""
Fiscal Intelligence Dashboard for Policy Impact
10Alytics Hackathon: Transforming Fiscal Data into Actionable Insights
"""

import json
import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

DATA_DIR = Path("data/processed")
FOCUS_COUNTRIES = ["Nigeria", "Ghana", "Kenya", "South Africa", "Egypt"]

# Page configuration
st.set_page_config(
    page_title="Fiscal Intelligence for Policy Impact | 10Alytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
        <style>
        .stApp {
        background-color: #F8FAFB;
        }

    footer {visibility: hidden;}
    .stDeployButton {display:none;}

        [data-testid="stSidebar"] {
            background-color: white;
        border-right: 2px solid #E2E8F0;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
    }

    .metric-card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    .sdg-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .sdg-1, .sdg-2 { background: #E5243B; color: white; }
    .sdg-8, .sdg-9 { background: #A21942; color: white; }
    .sdg-16, .sdg-17 { background: #00689D; color: white; }

    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid;
    }

    .alert-danger {
        background: #FEF2F2;
        border-color: #EF4444;
        color: #7F1D1D;
    }

    .alert-success {
        background: #ECFDF5;
        border-color: #10B981;
        color: #065F46;
    }

    .section-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }

    .insight-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    </style>
""",
            unsafe_allow_html=True)

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
            "title": "Public wage bill is widening deficits",
            "action":
            "Freeze non-essential public hiring and digitise payroll to eliminate ghost workers; redirect savings into capital projects.",
            "target": lambda current:
            f"Reduce wage bill share from {format_pct(current)} to {format_pct(max(current - 0.01, 0), 1)} by FY2027.",
            "timeline": "0–24 months",
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
        cards.append(
            {
                "Country": country,
                "Narrative": template["title"],
                "Finding": f"β = {
                    best['beta']:.2f} with R² {
                    best['r_squared']:.2f}. Every 1pp change in this driver shifts the deficit meaningfully.",
                "Action": template["action"],
                "Target": template["target"](current_metric),
                "Timeline": template["timeline"],
            })
    return cards


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

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0; border-bottom: 2px solid #E2E8F0;">
            <h1 style="font-size: 1.5rem; font-weight: 700; color: #0F172A; margin: 0;">
                📊 Fiscal Intelligence
            </h1>
            <p style="font-size: 0.875rem; color: #64748B; margin: 0.5rem 0 0 0;">
                10Alytics Hackathon
            </p>
        </div>
    """,
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation
    st.markdown("### 🎯 Navigate Dashboard")
    page = st.radio(
        "Select View",
        [
            "📊 Overview",
            "🧮 Driver Analysis",
            "⚠️ Risk & Forecast",
            "📋 Recommendations",
            "📑 Limitations & Data Quality",
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
st.markdown("""
    <div style="padding: 0 0 2rem 0;">
        <h1 style="font-size: 3rem; font-weight: 800; color: #0F172A; margin: 0;">
            Fiscal Intelligence for Policy Impact
        </h1>
        <p style="font-size: 1.25rem; color: #64748B; margin: 0.5rem 0 0 0;">
            Evidence-Based Solutions for Sustainable Development Across Africa
            </p>
        </div>
""",
            unsafe_allow_html=True)

# Render pages
if page == "📊 Overview":
    st.markdown('<div class="section-header">🌍 Executive Dashboard</div>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    if not scorecard.empty:
        with col1:
            median_debt = scorecard["Debt_to_GDP"].median() * 100
            st.markdown(
                f"""
                <div class="metric-card">
                    <p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 0.5rem;">
                        Median Debt-to-GDP
                    </p>
                    <h2 style="font-size: 2.5rem; font-weight: 800; color: #0F172A; margin: 0;">
                        {median_debt:.1f}%
                    </h2>
                    <p style="font-size: 0.875rem; color: #64748B; margin: 0.5rem 0 0 0;">
                        🔴 High risk: >90%
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            high_risk = int((scorecard["Debt_to_GDP"] > 0.9).sum())
            st.markdown(
                f"""
                <div class="metric-card">
                    <p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 0.5rem;">
                        High Risk Countries
                    </p>
                    <h2 style="font-size: 2.5rem; font-weight: 800; color: #EF4444; margin: 0;">
                        {high_risk}
                    </h2>
                    <p style="font-size: 0.875rem; color: #64748B; margin: 0.5rem 0 0 0;">
                        Exceeding 90% threshold
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            weak_revenue = int((scorecard["Revenue_to_GDP"] < 0.18).sum())
            st.markdown(
                f"""
                <div class="metric-card">
                    <p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 0.5rem;">
                        Weak Revenue Base
                    </p>
                    <h2 style="font-size: 2.5rem; font-weight: 800; color: #F59E0B; margin: 0;">
                        {weak_revenue}
                    </h2>
                    <p style="font-size: 0.875rem; color: #64748B; margin: 0.5rem 0 0 0;">
                        Below 18% target
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            high_inflation = int((scorecard["Inflation Rate"] > 10).sum())
            st.markdown(
                f"""
                <div class="metric-card">
                    <p style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 0.5rem;">
                        Inflation Pressure
                    </p>
                    <h2 style="font-size: 2.5rem; font-weight: 800; color: #EF4444; margin: 0;">
                        {high_inflation}
                    </h2>
                    <p style="font-size: 0.875rem; color: #64748B; margin: 0.5rem 0 0 0;">
                        Above 10% inflation
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Fiscal Stress Landscape</div>',
                unsafe_allow_html=True)
    if not scorecard.empty:
        focus_countries = FOCUS_COUNTRIES
        focus_scorecard = scorecard[scorecard["Country"].isin(focus_countries)]
        fig = go.Figure()
        colors = {
            "Nigeria": "#e74c3c",
            "Egypt": "#3498db",
            "Ghana": "#2ecc71",
            "Kenya": "#f39c12",
            "South Africa": "#9b59b6",
        }
        for country in focus_countries:
            row = focus_scorecard[focus_scorecard["Country"] == country]
            if row.empty:
                continue
            latest = row.iloc[0]
            if pd.notna(latest["Revenue_to_GDP"]) and pd.notna(
                    latest["Debt_to_GDP"]):
                fig.add_trace(
                    go.Scatter(
                        x=[latest["Revenue_to_GDP"] * 100],
                        y=[latest["Debt_to_GDP"] * 100],
                        mode="markers+text",
                        name=country,
                        text=country,
                        textposition="top center",
                        marker=dict(
                            size=20,
                            color=colors.get(country, "#95a5a6"),
                            line=dict(color="white", width=2),
                        ),
                        hovertemplate=(f"<b>{country}</b><br>"
                                       "Revenue/GDP: %{x:.1f}%<br>"
                                       "Debt/GDP: %{y:.1f}%<extra></extra>"),
                    ))
        fig.add_hline(y=90,
                      line_dash="dash",
                      line_color="red",
                      annotation_text="90% Debt/GDP Threshold")
        fig.add_vline(x=25,
                      line_dash="dash",
                      line_color="green",
                      annotation_text="25% Revenue/GDP Target")
        fig.update_layout(
            title="Debt Burden vs. Revenue Mobilisation",
            xaxis_title="Revenue to GDP (%)",
            yaxis_title="Debt to GDP (%)",
            height=500,
            showlegend=False,
            hovermode="closest",
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div class="insight-panel">
                <h3 style="font-size: 1.5rem; font-weight: 700; margin: 0 0 1rem 0;">
                    💡 Key Insights
                </h3>
                <ul style="font-size: 1rem; line-height: 1.8;">
                    <li><b>Egypt</b> remains above the 90% debt-to-GDP danger zone and needs near-term reprofiling.</li>
                    <li><b>Nigeria & Ghana</b> still collect below 20% of GDP in revenue, constraining fiscal buffers.</li>
                    <li><b>Revenue volatility</b> is a primary deficit driver across focus countries (see Driver Analysis).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 Fiscal Trends</div>',
                unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["💰 Revenue", "📊 Debt", "🔥 Inflation"])

    with tab1:
        revenue_df = filtered_df[filtered_df["Indicator"] == "Revenue"]
        if not revenue_df.empty:
            fig = px.line(
                revenue_df,
                x="Year",
                y="Amount_standardised",
                color="Country",
                title="Government Revenue Trends",
                labels={"Amount_standardised": "Revenue (Billions)"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data available for selected filters.")

    with tab2:
        debt_df = filtered_df[filtered_df["Indicator"] == "Government Debt"]
        if not debt_df.empty:
            fig = px.line(
                debt_df,
                x="Year",
                y="Amount_standardised",
                color="Country",
                title="Government Debt Accumulation",
                labels={"Amount_standardised": "Debt (Billions)"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No debt data available for selected filters.")

    with tab3:
        inflation_df = filtered_df[filtered_df["Indicator"] ==
                                   "Inflation Rate"]
        if not inflation_df.empty:
            fig = px.line(
                inflation_df,
                x="Year",
                y="Amount_numeric",
                color="Country",
                title="Inflation Rate Evolution",
                labels={"Amount_numeric": "Inflation Rate (%)"},
            )
            fig.add_hline(y=10,
                          line_dash="dash",
                          line_color="red",
                          annotation_text="10% Warning")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No inflation data available for selected filters.")

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
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(subset[[
                "coefficient", "beta", "p_value", "r_squared", "n_obs"
            ]],
                use_container_width=True)
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
        st.dataframe(anomalies_df, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
            title=f"{forecast_country}: {
                metric_choice.replace(
                    '_',
                    ' ').title()} outlook",
            yaxis_title="Percent of GDP")
        st.plotly_chart(fig, use_container_width=True)

elif page == "📋 Recommendations":
    st.markdown(
        '<div class="section-header">📋 Actionable Recommendations</div>',
        unsafe_allow_html=True)
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

elif page == "📑 Limitations & Data Quality":
    st.markdown('<div class="section-header">📑 Dataset Limitations & QA</div>',
                unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records",
                  f"{quality_report.get('total_records', len(df)):,}")
    with col2:
        st.metric("Countries", df['Country'].nunique() if not df.empty else 0)
    with col3:
        st.metric("Duplicates Resolved",
                  quality_report.get("duplicates_resolved", 0))
    with col4:
        st.metric("Manual Review Pending",
                  quality_report.get("duplicates_manual_review", 0))

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
            📊 10Alytics Hackathon
        </h3>
        <p style="font-size: 1.125rem; margin: 0;">
            Transforming Fiscal Data into Sustainable Development Solutions
        </p>
        </div>
""",
            unsafe_allow_html=True)
