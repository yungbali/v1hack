"""
Pan-African analytics UI components.

This module centralizes reusable HTML-driven Streamlit components that
power the hero metadata cards and reform scenario summary cards shown
across the dashboard. Keeping them here avoids duplication and ensures
both the overview page and the simulator share identical styling.
"""

from textwrap import dedent
from typing import Dict, List, Optional

import streamlit as st


def render_pan_african_metadata_cards(
    scope: str = "Pan-African macro-fiscal analytics",
    users: str = "Ministries, IFIs, CSOs, media",
    focus: str = "Risk, creditors, opportunity cost",
    status_label: str = "In active design",
    status_indicator_color: str = "#2ECC71",
    status_text_color: str = "#059669",
) -> None:
    """
    Render the four-panel metadata block for the Pan-African analytics hero.

    Args:
        scope: Description of the analytics scope.
        users: Primary audience segments.
        focus: Thematic focus areas.
        status_label: Current delivery or design status text.
        status_indicator_color: Hex color for the status dot.
        status_text_color: Hex color for the status text.
    """
    st.markdown(
        dedent(
            f"""
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <!-- Scope card -->
                <div style="border-radius: 0.5rem; border: 1px solid #E2E8F0; background: white; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Scope
                    </p>
                    <p style="font-size: 0.875rem; font-weight: 500; color: #0F172A;">
                        {scope}
                    </p>
                </div>

                <!-- Users card -->
                <div style="border-radius: 0.5rem; border: 1px solid #E2E8F0; background: white; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Users
                    </p>
                    <p style="font-size: 0.875rem; font-weight: 500; color: #0F172A;">
                        {users}
                    </p>
                </div>

                <!-- Focus card -->
                <div style="border-radius: 0.5rem; border: 1px solid #E2E8F0; background: white; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Focus
                    </p>
                    <p style="font-size: 0.875rem; font-weight: 500; color: #0F172A;">
                        {focus}
                    </p>
                </div>

                <!-- Status card -->
                <div style="border-radius: 0.5rem; border: 1px solid #E2E8F0; background: white; padding: 0.75rem;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Status
                    </p>
                    <p style="display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.875rem; font-weight: 500; color: {status_text_color}; margin: 0;">
                        <span style="height: 0.375rem; width: 0.375rem; border-radius: 9999px; background: {status_indicator_color};"></span>
                        {status_label}
                    </p>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_objective_banner(
    objective_text: str = (
        "Utilize the fiscal datasets to detect patterns, surface debt risks, and craft "
        "evidence-backed restructuring strategies that keep essential social services funded. "
        "Track deficits, creditor mixes, and spending trends across countries to equip policymakers "
        "with actionable insights."
    ),
    title: str = "Objective",
) -> None:
    """Render a branded banner summarizing the hackathon objective."""
    st.markdown(
        dedent(
            f"""
            <div style="margin: 1rem 0 2rem 0; padding: 1.5rem 1.75rem; border-radius: 0.75rem;
                        background: linear-gradient(135deg, #F97316, #EA580C);
                        color: white; border: 1px solid rgba(255, 255, 255, 0.15);">
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-start;">
                    <div style="flex: 1 1 240px;">
                        <span style="display: inline-flex; padding: 0.25rem 0.75rem; border-radius: 9999px;
                                     background: rgba(15, 23, 42, 0.18); font-size: 0.7rem; font-weight: 600;
                                     text-transform: uppercase; letter-spacing: 0.14em;">
                            {title}
                        </span>
                        <h3 style="font-size: 1.5rem; font-weight: 700; margin: 0.75rem 0 0.5rem 0;
                                   letter-spacing: -0.02em;">
                            Build policy-ready analytics for debt resilience
                        </h3>
                        <p style="font-size: 0.95rem; line-height: 1.7; margin: 0;">
                            {objective_text}
                        </p>
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_reform_results_summary(
    instant_impact_value: float,
    payment_reduction_pct: float,
    new_annual_debt_service: float,
    debt_to_gdp_year5: float,
    fiscal_space_freed_value: float,
    currency_prefix: str = "$",
    unit_suffix: str = "B",
    value_decimals: int = 2,
    percentage_decimals: int = 1,
    subtitle: Optional[str] = "freed annually",
    payment_copy: Optional[str] = "reduction in annual payments",
    fiscal_space_subcopy: Optional[str] = "Available for social spending",
) -> None:
    """
    Render the reform scenario summary card used in simulator results.

    Args:
        instant_impact_value: Monetary amount representing fiscal space impact (in billions by default).
        payment_reduction_pct: Percentage reduction in annual payments.
        new_annual_debt_service: Projected annual debt service (in billions by default).
        debt_to_gdp_year5: Projected debt-to-GDP ratio.
        fiscal_space_freed_value: Monetary value of fiscal space freed (in billions by default).
        currency_prefix: Currency symbol to prepend to monetary values.
        unit_suffix: Suffix appended to monetary values (e.g., "B" for billions).
        value_decimals: Decimal precision for monetary values.
        percentage_decimals: Decimal precision for percentage metrics.
        subtitle: Optional subtitle shown under the instant impact figure.
        payment_copy: Copy shown under the instant impact percentage reduction.
        fiscal_space_subcopy: Copy shown under the fiscal space freed metric.
    """

    def _format_value(value: float) -> str:
        return f"{currency_prefix}{value:,.{value_decimals}f}{unit_suffix}"

    instant_impact = _format_value(instant_impact_value)
    new_annual_payment = _format_value(new_annual_debt_service)
    fiscal_space = _format_value(fiscal_space_freed_value)
    payment_reduction = f"{payment_reduction_pct:.{percentage_decimals}f}%"

    st.markdown(
        dedent(
            f"""
            <div style="border-radius: 0.75rem; border: 1px solid #BBF7D0; background: linear-gradient(to bottom, #F0FDF4, #DCFCE7); padding: 1.5rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">
                        Reform scenario results
                    </h3>
                    <span style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.25rem 0.5rem; background: white; border: 1px solid #BBF7D0; border-radius: 0.25rem; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.14em; color: #15803D;">
                        Projected
                    </span>
                </div>

                <!-- Instant Impact Summary -->
                <div style="background: white; border: 1px solid #BBF7D0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                        Instant impact
                    </p>
                    <div style="display: flex; align-items: baseline; gap: 0.5rem;">
                        <p style="font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: #15803D; margin: 0;">
                            {instant_impact}
                        </p>
                        <span style="font-size: 0.875rem; color: #64748B;">{subtitle or ""}</span>
                    </div>
                    <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.25rem;">
                        {payment_reduction} {payment_copy or ""}
                    </p>
                </div>

                <!-- Metric 1: New Annual Payment -->
                <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #BBF7D0;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        New annual debt service
                    </p>
                    <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                        {new_annual_payment}
                    </p>
                </div>

                <!-- Metric 2: New Debt-to-GDP -->
                <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #BBF7D0;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Debt-to-GDP (Year 5)
                    </p>
                    <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                        {debt_to_gdp_year5:.1f}%
                    </p>
                </div>

                <!-- Metric 3: Fiscal Space Freed -->
                <div>
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Fiscal space freed
                    </p>
                    <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #15803D; margin: 0;">
                        {fiscal_space}
                    </p>
                    <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.25rem;">
                        {fiscal_space_subcopy or ""}
                    </p>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_opportunity_cost_summary(
    panel_data: Dict[str, Dict[str, object]],
    title: str,
    subtitle: Optional[str] = None,
) -> None:
    """Render a consistent grid of opportunity-cost tiles."""
    if not panel_data:
        return

    order = ['schools', 'hospitals', 'vaccine_doses', 'teachers']
    tiles = []

    for key in order:
        entry = panel_data.get(key)
        if not entry:
            continue
        tiles.append(
            f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white;
                        padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem;
                        text-align: left;">
                <div style="height: 3rem; width: 3rem; border-radius: 0.5rem;
                            background: rgba(15, 23, 42, 0.05); display: flex; align-items: center;
                            justify-content: center; font-size: 1.5rem;">
                    {entry.get('emoji', '📊')}
                </div>
                <div>
                    <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0 0 0.25rem 0;">
                        {entry.get('quantity', 0):,}
                    </p>
                    <p style="font-size: 0.875rem; font-weight: 500; color: #475569; margin: 0 0 0.25rem 0;">
                        {entry.get('label', '').strip()}
                    </p>
                    <p style="font-size: 0.7rem; color: #64748B; margin: 0;">
                        @ ${int(entry.get('unit_cost', 0)):,} each
                    </p>
                </div>
            </div>
            """
        )

    grid_html = "".join(tiles)

    st.markdown(
        dedent(
            f"""
            <div style="margin: 1.5rem 0; padding: 1.25rem; background: #F8FAFC; border-radius: 0.75rem;
                        border: 1px solid #E2E8F0;">
                <div style="margin-bottom: 1rem;">
                    <p style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin: 0 0 0.5rem 0;">
                        {title}
                    </p>
                    {"<p style='font-size:0.85rem; color:#475569; margin:0;'>" + subtitle + "</p>" if subtitle else ""}
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                    {grid_html}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_recommendations_panel(
    recommendations: List[Dict[str, str]],
    title: str = "Recommended next steps",
    intro: Optional[str] = None,
) -> None:
    """Render a structured list of recommendations for analysts."""
    if not recommendations:
        return

    items_html = "".join(
        [
            f"""
            <li style="margin-bottom: 0.75rem;">
                <span style="display: block; font-size: 0.9rem; font-weight: 600; color: #0F172A;">
                    {item.get('title', 'Recommendation')}
                </span>
                <span style="display: block; font-size: 0.85rem; color: #475569; line-height: 1.6;">
                    {item.get('description', '').strip()}
                </span>
            </li>
            """
            for item in recommendations
        ]
    )

    st.markdown(
        dedent(
            f"""
            <div style="margin: 1.5rem 0 0 0; padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #E2E8F0;
                        background: white;">
                <p style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin: 0 0 0.5rem 0;">
                    {title}
                </p>
                {"<p style='font-size:0.85rem; color:#475569; margin:0 0 1rem 0;'>" + intro + "</p>" if intro else ""}
                <ul style="list-style: none; padding: 0; margin: 0;">
                    {items_html}
                </ul>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
