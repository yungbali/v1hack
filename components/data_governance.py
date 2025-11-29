import streamlit as st
import pandas as pd
import os
from datetime import datetime

def clean_html(html: str) -> str:
    """Remove all leading whitespace from each line to avoid Markdown code blocks."""
    return "\n".join(line.strip() for line in html.splitlines())

def load_manual_review_data():
    """Loads the duplicates file for manual review."""
    path = "data/processed/fiscal_duplicates_manual_review.csv"
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

def load_resolution_log():
    """Loads the resolution log or creates an empty one."""
    path = "data/processed/fiscal_duplicate_resolution_log.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["country", "indicator", "year", "action", "kept_value", "timestamp", "user_comment"])

def save_resolution(resolution_data):
    """Appends a resolution to the log file."""
    path = "data/processed/fiscal_duplicate_resolution_log.csv"
    
    # Convert to DataFrame
    new_entry = pd.DataFrame([resolution_data])
    
    if os.path.exists(path):
        new_entry.to_csv(path, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(path, index=False)

def render_manual_review_interface():
    """Renders the AI-Assisted Data Governance & Manual Review interface."""
    
    st.markdown(clean_html("""
        <div class="mb-6">
            <h2 class="text-2xl font-bold text-gray-800">🛠️ AI-Assisted Data Governance</h2>
            <p class="text-gray-600">
                Review and resolve data anomalies flagged by the AI pre-screening engine. 
                Your decisions retrain the matching model for higher accuracy.
            </p>
        </div>
    """), unsafe_allow_html=True)

    # Load data
    df = load_manual_review_data()
    if df is None or df.empty:
        st.success("✅ No pending manual reviews! The queue is empty.")
        return

    # Load existing resolutions to filter out already resolved items
    log_df = load_resolution_log()
    
    # Group by potential duplicate keys
    # Assuming duplicates share Country, Indicator, Year
    # We create a composite key for identifying clusters
    df['cluster_id'] = df['Country'] + "|" + df['Indicator'] + "|" + df['Year'].astype(str)
    
    # Filter out clusters that have been resolved
    if not log_df.empty:
        # Create matching keys in log_df
        # Note: We need to ensure column names match or map them correctly
        log_df['cluster_id'] = log_df['country'] + "|" + log_df['indicator'] + "|" + log_df['year'].astype(str)
        resolved_ids = set(log_df['cluster_id'].unique())
        df = df[~df['cluster_id'].isin(resolved_ids)]

    if df.empty:
        st.success("✅ All flagged items have been resolved!")
        return

    # Get unique clusters
    unique_clusters = df['cluster_id'].unique()
    total_clusters = len(unique_clusters)
    
    st.markdown(clean_html(f"""
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
            <div class="flex items-center">
                <span class="text-2xl mr-2">🤖</span>
                <div>
                    <p class="font-bold text-blue-800">AI Pre-Screening Status</p>
                    <p class="text-sm text-blue-700">
                        <span class="font-bold">{total_clusters}</span> clusters flagged for human review. 
                        Confidence scores indicate potential duplicates vs. distinct entities.
                    </p>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # Queue Navigation
    if 'current_cluster_index' not in st.session_state:
        st.session_state.current_cluster_index = 0
    
    # Ensure index is valid
    if st.session_state.current_cluster_index >= total_clusters:
        st.session_state.current_cluster_index = 0

    current_cluster_id = unique_clusters[st.session_state.current_cluster_index]
    cluster_data = df[df['cluster_id'] == current_cluster_id]
    
    # Extract metadata from the first row of the cluster
    meta = cluster_data.iloc[0]
    
    # Progress Bar
    progress = (st.session_state.current_cluster_index + 1) / total_clusters
    st.progress(progress)
    st.caption(f"Reviewing item {st.session_state.current_cluster_index + 1} of {total_clusters}")

    # UI Layout for Comparison
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🏳️ {meta['Country']}")
        st.markdown(f"**Indicator:** {meta['Indicator']}")
        st.markdown(f"**Year:** {int(meta['Year'])}")
        st.markdown(f"**Source:** {meta.get('Source', 'Unknown')}")
    
    with col2:
        st.markdown("### ⚠️ AI Confidence")
        # Mock confidence score based on relative diff
        diff = cluster_data['relative_diff'].mean() if 'relative_diff' in cluster_data.columns else 0.5
        confidence = max(0, min(100, int((1 - diff) * 100)))
        
        color = "red"
        if confidence > 80: color = "green"
        elif confidence > 50: color = "orange"
        
        st.markdown(clean_html(f"""
            <div class="text-center p-4 bg-white rounded shadow">
                <div class="text-3xl font-bold text-{color}-600">{confidence}%</div>
                <div class="text-xs text-gray-500">Duplicate Probability</div>
            </div>
        """), unsafe_allow_html=True)

    st.divider()

    # Display Candidates
    st.markdown("#### 🔎 Candidate Records")
    
    # Custom CSS for the selection cards
    st.markdown("""
        <style>
        .candidate-card {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .candidate-card:hover {
            border-color: #3b82f6;
            background-color: #eff6ff;
        }
        </style>
    """, unsafe_allow_html=True)

    # Show candidates in columns
    cols = st.columns(len(cluster_data))
    
    selected_value = None
    
    for idx, (i, row) in enumerate(cluster_data.iterrows()):
        with cols[idx % len(cols)]: # Wrap if too many
            st.markdown(clean_html(f"""
                <div class="candidate-card">
                    <div class="font-bold text-lg">Option {chr(65+idx)}</div>
                    <div class="text-2xl font-mono my-2">{row['Amount']:,.2f}</div>
                    <div class="text-sm text-gray-600">
                        Unit: {row.get('Unit', 'N/A')}<br>
                        Source: {row.get('Source', 'N/A')}
                    </div>
                </div>
            """), unsafe_allow_html=True)
            
            if st.button(f"Keep Option {chr(65+idx)}", key=f"btn_keep_{i}"):
                resolve_conflict(meta, "keep", row['Amount'], f"Selected Option {chr(65+idx)}")
                st.rerun()

    st.divider()
    
    # Action Bar
    ac1, ac2, ac3 = st.columns(3)
    
    with ac1:
        if st.button("🧮 Average Values", use_container_width=True):
            avg_val = cluster_data['Amount'].mean()
            resolve_conflict(meta, "average", avg_val, "Averaged all candidates")
            st.rerun()
            
    with ac2:
        if st.button("❌ Not Duplicates (Keep All)", use_container_width=True):
            resolve_conflict(meta, "keep_all", None, "Marked as distinct records")
            st.rerun()
            
    with ac3:
        if st.button("⏩ Skip for Now", use_container_width=True):
            st.session_state.current_cluster_index += 1
            st.rerun()

def resolve_conflict(meta, action, value, comment):
    """Handles the resolution logic and logging."""
    
    resolution = {
        "country": meta['Country'],
        "indicator": meta['Indicator'],
        "year": meta['Year'],
        "action": action,
        "kept_value": value,
        "timestamp": datetime.now().isoformat(),
        "user_comment": comment
    }
    
    save_resolution(resolution)
    
    # Move to next item
    st.session_state.current_cluster_index += 1
    st.toast(f"✅ Resolved: {comment}")

if __name__ == "__main__":
    render_manual_review_interface()

