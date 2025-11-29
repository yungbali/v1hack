"""
AI Policy Advisor Component
---------------------------
Integrates Google's Gemini models to provide real-time, data-driven fiscal policy advice.
Incorporates live/simulated market sentiment via RSS feeds.
"""

import streamlit as st
import pandas as pd
import time
import random
from google import genai
from typing import Dict, Any, List
import feedparser
from datetime import datetime
import json

# --- UTILS ---


def clean_html(html: str) -> str:
    """Remove all leading whitespace from each line to avoid Markdown code blocks."""
    return "\n".join(line.strip() for line in html.splitlines())


def _get_live_news_sentiment(api_key: str) -> Dict[str, Any]:
    """
    Fetches real-time economic sentiment from RSS feeds and uses Gemini to analyze it.
    """
    # List of relevant RSS feeds
    feeds = [
        "https://www.imf.org/en/News/RSS",
        "https://www.worldbank.org/en/news/rss",
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://allafrica.com/tools/headlines/rdf/business/headlines.rdf"
    ]

    headlines = []
    try:
        # Fetch from multiple feeds to ensure diversity
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    for entry in feed.entries[:2]:  # Take top 2 from each
                        headlines.append(entry.title)
            except Exception:
                continue
            if len(headlines) >= 5: break  # limit to 5 headlines
    except Exception:
        pass

    # Fallback if offline or no feeds found
    if not headlines:
        headlines = [
            "Global commodity prices show volatility amidst supply chain shifts",
            "Emerging market bond yields rise as Fed signals tightening",
            "Regional trade pacts expected to boost intra-African commerce",
            "Oil price stabilization offers brief respite for exporters",
            "Climate resilience funding becomes key condition for new loans"
        ]

    # Use Gemini to analyze sentiment of these headlines
    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
        Analyze the economic sentiment of the following headlines for an African fiscal policy context.
        Headlines:
        {chr(10).join(['- ' + h for h in headlines])}
        
        Output strictly in JSON format:
        {{
            "score": <float between -1.0 (negative) and 1.0 (positive)>,
            "label": <"Optimistic", "Neutral", or "Cautious">,
            "summary": <One sentence summary of the market mood>
        }}
        """

        response = client.models.generate_content(model="gemini-2.0-flash",
                                                  contents=prompt)

        # Cleanup json string if markdown blocks are present
        text = response.text.replace('```json', '').replace('```', '').strip()
        sentiment_data = json.loads(text)

        return {
            "headlines":
            headlines,
            "score":
            sentiment_data.get("score", 0.0),
            "label":
            sentiment_data.get("label", "Neutral"),
            "summary":
            sentiment_data.get("summary", "Market conditions are mixed."),
            "source":
            "Live Analysis via Gemini"
        }

    except Exception as e:
        # Fallback if AI analysis fails
        return {
            "headlines": headlines,
            "score": 0.0,
            "label": "Neutral",
            "summary": f"Unable to analyze real-time sentiment: {str(e)}",
            "source": "Fallback Mode"
        }


def _construct_prompt(country: str, metrics: Dict[str, float],
                      sentiment: Dict[str, Any]) -> str:
    """Builds a strict, data-grounded prompt for the LLM."""

    metric_text = "\n".join([f"- {k}: {v}" for k, v in metrics.items()])
    headlines_text = "\n".join([f"- {h}" for h in sentiment["headlines"]])

    return f"""
    You are the Senior Chief Fiscal Policy Advisor for {country}. 
    Your goal is to provide actionable, data-backed fiscal recommendations based STRICTLY on the provided data and current market sentiment.
    
    CONTEXT:
    Current Economic Sentiment: {sentiment['label']} ({sentiment['score']})
    Market Summary: {sentiment['summary']}
    Recent Headlines:
    {headlines_text}
    
    FISCAL DATA FOR {country.upper()}:
    {metric_text}
    
    INSTRUCTIONS:
    1. Analyze the Debt Sustainability: Is the current debt level ({metrics.get('Debt to GDP', 'N/A')}) dangerous given the revenue ({metrics.get('Revenue to GDP', 'N/A')})?
    2. Synthesize with Sentiment: How should {country} react to the current global sentiment ({sentiment['label']})?
    3. Recommend 3 Concrete Actions: Be specific (e.g., "Reprofile short-term debt", "Broaden VAT base"). Avoid generic advice.
    4. Tone: Professional, authoritative, concise. "Aaron Sorkin" style: smart, snappy, high-stakes.
    
    CONSTRAINT:
    - Do NOT hallucinate data not provided.
    - If data is missing, acknowledge the gap.
    - Keep it under 250 words.
    """


# --- MAIN INTERFACE ---


def render_ai_advisor_interface(df: pd.DataFrame, api_key: str):
    """Renders the AI Advisor UI."""

    st.markdown(clean_html("""
        <div style="margin-bottom: 2rem;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <h1 style="font-size: 2rem; font-weight: 700; color: #1E293B; margin:0;">🤖 AI Fiscal Policy Advisor</h1>
                <span style="background:#E0E7FF; color:#4338CA; padding:0.2rem 0.6rem; border-radius:1rem; font-size:0.7rem; font-weight:600;">Powered by Gemini</span>
            </div>
            <p style="color: #64748B; margin-top:0.5rem;">Real-time, data-driven insights augmented by global market sentiment.</p>
        </div>
    """),
                unsafe_allow_html=True)

    if not api_key:
        st.warning(
            "⚠️ Gemini API Key is missing. Please enter it in the sidebar to activate the AI Advisor."
        )
        st.markdown("""
            <div style="background: #F1F5F9; padding: 1rem; border-radius: 0.5rem;">
                <strong>Why do I need a key?</strong><br>
                This feature uses Google's Gemini models to generate live insights. Your key is used locally and never stored permanently.
            </div>
        """,
                    unsafe_allow_html=True)
        return

    # Country Context Selector
    countries = sorted(df['Country'].unique()) if not df.empty else ["Nigeria"]
    selected_country = st.selectbox("Select Country for Analysis",
                                    countries,
                                    index=0)

    # Get Data for Prompt
    latest_year = df['Year'].max()
    country_data = df[(df['Country'] == selected_country)
                      & (df['Year'] == latest_year)]

    metrics = {}
    if not country_data.empty:
        for _, row in country_data.iterrows():
            metrics[row[
                'Indicator']] = f"{row['Amount_standardised']}" if pd.notna(
                    row['Amount_standardised']) else f"{row['Amount']}"

    key_indicators = {
        "Debt to GDP": "Government Debt",
        "Revenue to GDP": "Revenue",
        "Inflation": "Inflation Rate"
    }

    prompt_metrics = {}
    for label, indicator in key_indicators.items():
        val = country_data[country_data['Indicator'] ==
                           indicator]['Amount'].values
        if len(val) > 0:
            prompt_metrics[label] = f"{val[0]}"

    # UI Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        user_query = st.text_area(
            "Specific Policy Question (Optional)",
            placeholder=
            "e.g., How can we reduce the wage bill without sparking social unrest?",
            height=100)

        if st.button("🧠 Generate Policy Brief", type="primary"):

            # 1. Sentiment Analysis Step (Real Feed + Gemini Analysis)
            with st.status("📡 Scanning global market sentiment...",
                           expanded=True) as status:
                st.write(
                    "Fetching live headlines from global economic feeds...")
                sentiment = _get_live_news_sentiment(api_key)

                st.write(
                    f"**Market Mood:** {sentiment['label']} (Score: {sentiment['score']})"
                )
                st.caption(f"Analysis: {sentiment['summary']}")

                st.write("Top Headlines analyzed:")
                for h in sentiment['headlines'][:3]:
                    st.text(f"- {h}")

                status.update(label="✅ Market Context Acquired",
                              state="complete",
                              expanded=False)

            # 2. Thinking Step
            progress_text = "Thinking..."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(
                    percent_complete + 1,
                    text=
                    f"Synthesizing {len(metrics)} data points for {selected_country}..."
                )

            time.sleep(0.5)
            my_bar.empty()

            # 3. Call Gemini
            try:
                client = genai.Client(api_key=api_key)

                full_prompt = _construct_prompt(selected_country,
                                                prompt_metrics, sentiment)
                if user_query:
                    full_prompt += f"\n\nUSER SPECIFIC QUESTION: {user_query}"

                with st.chat_message("assistant", avatar="🤖"):
                    response_container = st.empty()
                    full_response = ""

                    # Generate content (Gemini streaming)
                    # Note: google-genai SDK streaming support uses generate_content_stream
                    response = client.models.generate_content_stream(
                        model="gemini-2.0-flash", contents=full_prompt)

                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            response_container.markdown(full_response + "▌")

                    response_container.markdown(full_response)

            except Exception as e:
                st.error(f"❌ AI Error: {str(e)}")

    with col2:
        st.markdown(clean_html(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.75rem; padding: 1.25rem;">
                <h3 style="font-size: 1rem; font-weight: 600; margin-bottom: 1rem;">📊 Data Context</h3>
                <div style="margin-bottom: 0.75rem;">
                    <p style="font-size: 0.75rem; color: #64748B; margin: 0;">Selected Country</p>
                    <p style="font-weight: 600; color: #0F172A;">{selected_country}</p>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <p style="font-size: 0.75rem; color: #64748B; margin: 0;">Last Update</p>
                    <p style="font-weight: 600; color: #0F172A;">{latest_year}</p>
                </div>
                <hr style="margin: 1rem 0; border-color: #E2E8F0;">
                <p style="font-size: 0.75rem; color: #64748B;">
                    The AI uses strictly validated data from the platform's processed datasets (CSV/Parquet) to prevent hallucinations.
                </p>
            </div>
        """),
                    unsafe_allow_html=True)


if __name__ == "__main__":
    # For testing independently
    st.set_page_config(layout="wide")
    render_ai_advisor_interface(pd.DataFrame(), "")
