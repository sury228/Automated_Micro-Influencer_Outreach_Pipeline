"""
Micro-Influencer Outreach System - High-Contrast Aligned Bold Theme
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DB_PATH, TARGET_NICHE, MIN_FOLLOWERS, MAX_FOLLOWERS, MIN_ENGAGEMENT_RATE
from src.database.models import get_stats, get_all_influencers, get_qualified_influencers, get_outreach_logs, clear_all_data
from src.pipeline import OutreachPipeline
from src.outreach.tracker import OutreachTracker

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS (Clean Typography without breaking Streamlit Icons)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Influencer Outreach Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High-Contrast Theme: Solid Black (#000000) Bold (700/800) Text with Icon Protection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');

    /* Global Text Override - Targeted without breaking Streamlit Material Icons */
    html, body, p, label, h1, h2, h3, h4, h5, h6, .stMarkdown, [data-testid="stMarkdownContainer"] p {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Preserve Streamlit Material Symbol Icons */
    [data-testid="stSidebarCollapseButton"] span, 
    [data-testid="stIcon"], 
    i, 
    .material-symbols-outlined, 
    .material-icons {
        font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Icons' !important;
        font-weight: normal !important;
    }

    .stApp {
        background: linear-gradient(135deg, #FBF8EF 0%, #F3ECE0 50%, #EAE0D0 100%);
        background-attachment: fixed;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* Hero Banner */
    .hero-container {
        background: #FFFFFF;
        border: 2.5px solid #D97706;
        border-radius: 18px;
        padding: 1.8rem 2.4rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(217, 119, 6, 0.25);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Metric Cards */
    .metric-card-wrapper {
        background: #FFFFFF;
        border: 2.5px solid #B45309;
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
        height: 100%;
    }
    .metric-card-wrapper:hover {
        transform: translateY(-3px);
        border-color: #D97706;
        box-shadow: 0 12px 24px -4px rgba(180, 83, 9, 0.3);
    }
    .metric-val {
        font-size: 2.7rem;
        font-weight: 900 !important;
        color: #000000 !important;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .metric-lbl {
        font-size: 0.88rem;
        font-weight: 800 !important;
        color: #000000 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
    }

    /* Clean Aligned Rule Cards for Tab 3 */
    .rule-card {
        background: #FFFFFF;
        border: 2.5px solid #D97706;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .rule-card-title {
        font-size: 0.95rem;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 0.5rem;
        white-space: nowrap;
    }
    .rule-card-value {
        font-size: 0.9rem;
        font-weight: 800 !important;
        color: #92400E !important;
        background: #FEF3C7;
        padding: 0.35rem 0.8rem;
        border-radius: 8px;
        border: 1px solid #F59E0B;
        display: inline-block;
        white-space: nowrap;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 800 !important;
        letter-spacing: 0.03em;
    }
    .badge-qualified {
        background: #D1FAE5;
        color: #065F46 !important;
        border: 2px solid #059669;
    }
    .badge-disqualified {
        background: #FEE2E2;
        color: #991B1B !important;
        border: 2px solid #DC2626;
    }

    /* Pitch Boxes */
    .pitch-box {
        background: #FFFFFF;
        border: 2.5px solid #D97706;
        border-radius: 14px;
        padding: 1.3rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1rem;
        line-height: 1.65;
        white-space: pre-wrap;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    /* Dataframe Overrides */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 2.5px solid #B45309 !important;
        padding: 4px !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: #FEF3C7 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stDataFrame"] td {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }

    /* Input & Select Box Text */
    input, select, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        font-weight: 700 !important;
        background-color: #FFFFFF !important;
        border: 2px solid #B45309 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F3ECE0;
        border-right: 2px solid #D97706;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #EAE0D0;
        padding: 8px;
        border-radius: 14px;
        border: 2px solid #B45309;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        border-radius: 10px;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 0.95rem;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #D97706 !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        box-shadow: 0 4px 14px rgba(180, 83, 9, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Helper Data Loaders
# -----------------------------------------------------------------------------
def load_data():
    """Load latest dataset from SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    df_all = pd.read_sql_query("SELECT * FROM influencers ORDER BY followers DESC", conn)
    df_logs = pd.read_sql_query("""
        SELECT ol.id, i.name, i.platform, i.email, ol.channel, ol.status, ol.sent_at, ol.created_at, ol.error_message
        FROM outreach_log ol
        JOIN influencers i ON ol.influencer_id = i.id
        ORDER BY ol.created_at DESC
    """, conn)
    conn.close()
    return df_all, df_logs


# -----------------------------------------------------------------------------
# 3. Sidebar Panel
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ Outreach Engine")
    st.markdown(f"**Target Niche:** `{TARGET_NICHE}`")
    st.markdown(f"**Filtering Rules:** `5K–100K Subs | ≥{MIN_ENGAGEMENT_RATE}% Eng`")
    st.divider()

    st.markdown("#### 🛠️ Pipeline Controls")

    if st.button("▶️ Execute Full Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Running discovery, qualification, enrichment, LLM pitch & outreach..."):
            pipeline = OutreachPipeline(simulate_email=True)
            res = pipeline.run_full_pipeline()
            if res.get("success"):
                st.toast(f"Pipeline completed in {res['duration']}s!", icon="✅")
                st.rerun()
            else:
                st.error(f"Error: {res.get('error')}")

    if st.button("🎲 Load 50 Demo Creators", use_container_width=True):
        with st.spinner("Populating 50 micro-influencer records..."):
            import subprocess
            subprocess.run([sys.executable, "run.py", "--action", "demo-data"], cwd=str(PROJECT_ROOT))
            st.toast("50 Demo Creators Loaded!", icon="🎉")
            st.rerun()

    if st.button("📥 Export All CSV Datasets", use_container_width=True):
        tracker = OutreachTracker()
        paths = tracker.export_all()
        st.toast("CSVs Exported to data/ and outputs/!", icon="💾")

    if st.button("🗑️ Reset Database", use_container_width=True):
        clear_all_data()
        st.toast("Database Cleared!", icon="🧹")
        st.rerun()

    st.divider()
    st.caption("Automated Influencer Outreach System")


# -----------------------------------------------------------------------------
# 4. Hero Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Automated Micro-Influencer Outreach Pipeline</div>
    <div class="hero-subtitle">
        AI Discovery • Rule-Based Qualification Audit • Profile Enrichment • Gemini LLM Personalization • Outreach Tracking
    </div>
</div>
""", unsafe_allow_html=True)

# Load data & statistics
df_all, df_logs = load_data()
stats = get_stats()


# -----------------------------------------------------------------------------
# 5. Top KPI Stat Cards
# -----------------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card-wrapper">
        <div class="metric-val">{stats['total_discovered']}</div>
        <div class="metric-lbl">Total Discovered</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card-wrapper">
        <div class="metric-val" style="color: #059669 !important;">{stats['qualified']}</div>
        <div class="metric-lbl">Qualified (5K–100K)</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card-wrapper">
        <div class="metric-val" style="color: #DC2626 !important;">{stats['disqualified']}</div>
        <div class="metric-lbl">Disqualified</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card-wrapper">
        <div class="metric-val">{stats['messages_generated']}</div>
        <div class="metric-lbl">AI Pitches Built</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card-wrapper">
        <div class="metric-val" style="color: #2563EB !important;">{stats['emails_sent']}</div>
        <div class="metric-lbl">Emails Sent / Logged</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. Tab Navigation Pages
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview & Analytics",
    "🔍 Discovered Influencers (50+)",
    "🎯 Qualification Audit Log",
    "💬 AI Personalization (Email & DM)",
    "✉️ Outreach Delivery Tracker",
])


# -----------------------------------------------------------------------------
# TAB 1: Overview & Analytics
# -----------------------------------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📈 Qualification Distribution")
        if stats["total_discovered"] > 0:
            status_df = pd.DataFrame({
                "Status": ["Qualified", "Disqualified", "Pending"],
                "Count": [stats["qualified"], stats["disqualified"], stats["pending_qualification"]],
            }).set_index("Status")
            st.bar_chart(status_df, color="#B45309", height=300)
        else:
            st.info("No creators discovered yet. Click **'🎲 Load 50 Demo Creators'** in the sidebar.")

    with col_right:
        st.markdown("### 👥 Top Creators by Subscriber Count")
        if not df_all.empty and "followers" in df_all.columns:
            top_df = df_all.head(10)[["name", "followers"]].set_index("name")
            st.bar_chart(top_df, color="#D97706", height=300)
        else:
            st.info("No follower metrics available.")

    st.markdown("### ⚡ End-to-End Pipeline Workflow Summary")
    st.dataframe(
        pd.DataFrame([
            {"Stage": "1. Influencer Discovery", "Method / Tool": "YouTube Data API v3 & Web Scraper", "Criteria": f"Niche: {TARGET_NICHE}", "Output": f"{stats['total_discovered']} Profiles Discovered"},
            {"Stage": "2. Qualification Audit", "Method / Tool": "Rule-Based Audit Engine", "Criteria": "5K–100K Subs, ≥2% Eng Rate, Tech Relevance", "Output": f"{stats['qualified']} Qualified Creators"},
            {"Stage": "3. Profile Enrichment", "Method / Tool": "Contact Extractor & Demographic Estimator", "Criteria": "Extract Business Email, Content Themes", "Output": f"{stats['total_discovered']} Enriched Profiles"},
            {"Stage": "4. AI Message Generation", "Method / Tool": "Google Gemini LLM (`gemini-2.0-flash`)", "Criteria": "60–90w Email Pitch + 15–30w Instagram DM", "Output": f"{stats['messages_generated']} Custom Messages"},
            {"Stage": "5. Outreach & Tracking", "Method / Tool": "SMTP Gmail Sender & SQLite Log", "Criteria": "Duplicate Prevention & Delivery Log", "Output": f"{stats['emails_sent']} Emails Delivered"},
        ]),
        use_container_width=True,
        hide_index=True,
    )


# -----------------------------------------------------------------------------
# TAB 2: Discovered Influencers Data Table
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("### 🔍 Complete Discovered Influencers Dataset")
    st.markdown("All 50+ influencer records with bold black readable text:")

    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_term = st.text_input("🔎 Search by Creator Name, Topic, Niche, or Email:", "", placeholder="Type name, python, sarah, etc...")
    with c_filter:
        status_sel = st.selectbox("Filter Status:", ["All Statuses", "QUALIFIED", "DISQUALIFIED", "PENDING"])

    view_df = df_all.copy()

    if status_sel != "All Statuses":
        view_df = view_df[view_df["qualification_status"] == status_sel]

    if search_term:
        st_low = search_term.lower()
        view_df = view_df[
            view_df["name"].str.lower().str.contains(st_low, na=False) |
            view_df["content_themes"].str.lower().str.contains(st_low, na=False) |
            view_df["email"].str.lower().str.contains(st_low, na=False) |
            view_df["niche"].str.lower().str.contains(st_low, na=False)
        ]

    st.markdown(f"**Showing {len(view_df)} Creator Records**")

    # Display all columns
    cols_to_show = [
        "name", "platform", "followers", "engagement_rate",
        "niche", "content_themes", "email", "qualification_status",
        "outreach_status", "audience_geography", "audience_age",
    ]
    avail_cols = [c for c in cols_to_show if c in view_df.columns]

    st.dataframe(
        view_df[avail_cols],
        use_container_width=True,
        hide_index=True,
        height=550,
        column_config={
            "name": st.column_config.TextColumn("Creator Name", width="medium"),
            "platform": st.column_config.TextColumn("Platform", width="small"),
            "followers": st.column_config.NumberColumn("Followers / Subs", format="%d", width="medium"),
            "engagement_rate": st.column_config.NumberColumn("Engagement Rate", format="%.2f%%", width="medium"),
            "niche": st.column_config.TextColumn("Niche", width="small"),
            "content_themes": st.column_config.TextColumn("Content Themes", width="medium"),
            "email": st.column_config.TextColumn("Contact Email", width="medium"),
            "qualification_status": st.column_config.TextColumn("Verdict", width="small"),
            "outreach_status": st.column_config.TextColumn("Outreach", width="small"),
            "audience_geography": st.column_config.TextColumn("Geography", width="small"),
            "audience_age": st.column_config.TextColumn("Audience Age", width="small"),
        },
    )


# -----------------------------------------------------------------------------
# TAB 3: Qualification Audit Log
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("### 🎯 Multi-Criteria Qualification & Filtering Audit Engine")
    st.markdown("Every influencer is audited against **4 quantitative criteria** before qualification:")

    # Clean 4-Card Equal Height Aligned Grid
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown("""
        <div class="rule-card">
            <div class="rule-card-title">Rule 1: Follower Range</div>
            <div class="rule-card-value">5,000 – 100,000 Subs</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown("""
        <div class="rule-card">
            <div class="rule-card-title">Rule 2: Engagement Rate</div>
            <div class="rule-card-value">≥ 2.0%</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown("""
        <div class="rule-card">
            <div class="rule-card-title">Rule 3: Tech Relevance</div>
            <div class="rule-card-value">AI / ML / Tech Keywords</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown("""
        <div class="rule-card">
            <div class="rule-card-title">Rule 4: Business Email</div>
            <div class="rule-card-value">Verified Email Present</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not df_all.empty:
        selected_creator = st.selectbox("Select Influencer to Inspect Detailed Audit Log:", df_all["name"].tolist())
        rec = df_all[df_all["name"] == selected_creator].iloc[0]

        a_col1, a_col2 = st.columns([1, 1])

        with a_col1:
            st.markdown(f"#### Creator Record: **{rec['name']}**")
            st.markdown(f"- **Platform:** `{rec['platform']}`")
            st.markdown(f"- **Subscribers / Followers:** `{rec['followers']:,}`")
            st.markdown(f"- **Engagement Rate:** `{rec['engagement_rate']}%`")
            st.markdown(f"- **Contact Email:** `{rec['email']}`")
            st.markdown(f"- **Content Themes:** `{rec['content_themes']}`")
            st.markdown(f"- **Estimated Audience Age:** `{rec.get('audience_age', '18-34')}`")
            st.markdown(f"- **Geography:** `{rec.get('audience_geography', 'Global')}`")

        with a_col2:
            st.markdown("#### Decision Audit Engine Output")
            verdict = rec.get("qualification_status", "PENDING")

            if verdict == "QUALIFIED":
                st.markdown('<span class="badge badge-qualified">VERDICT: QUALIFIED</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge badge-disqualified">VERDICT: DISQUALIFIED</span>', unsafe_allow_html=True)

            reason_log = rec.get("qualification_reason", "No audit log available.")
            st.code(reason_log, language="text")


# -----------------------------------------------------------------------------
# TAB 4: AI Personalization Preview (Email & DM)
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("### 💬 AI-Generated Personalized Collaboration Pitches")

    qual_df = df_all[df_all["qualification_status"] == "QUALIFIED"]

    if qual_df.empty:
        st.info("No qualified creators found. Run the pipeline or load demo data.")
    else:
        sel_name = st.selectbox("Select Qualified Creator for Message Inspection:", qual_df["name"].tolist())
        r = qual_df[qual_df["name"] == sel_name].iloc[0]

        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.markdown("#### 📧 Email Collaboration Pitch (60–90 Words)")
            email_text = r.get("email_message") or "No email message generated yet."
            st.markdown(f'<div class="pitch-box">{email_text}</div>', unsafe_allow_html=True)

        with p_col2:
            st.markdown("#### 💬 Instagram DM Pitch (15–30 Words)")
            dm_text = r.get("instagram_dm") or "No DM generated yet."
            st.markdown(f'<div class="pitch-box">{dm_text}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🧬 Personalization Signals Employed")
            st.markdown(f"- **Creator Name:** `{r.get('name')}`")
            st.markdown(f"- **Content Themes:** `{r.get('content_themes')}`")
            st.markdown(f"- **Recent Content Context:** `{str(r.get('recent_content'))[:100]}...`")


# -----------------------------------------------------------------------------
# TAB 5: Outreach Delivery Tracker
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("### ✉️ Outreach Sending Layer & Complete Delivery Log")

    if not df_logs.empty:
        st.dataframe(
            df_logs,
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                "id": st.column_config.NumberColumn("Log ID", width="small"),
                "name": st.column_config.TextColumn("Recipient Name", width="medium"),
                "platform": st.column_config.TextColumn("Platform", width="small"),
                "email": st.column_config.TextColumn("Email Address", width="medium"),
                "channel": st.column_config.TextColumn("Channel", width="small"),
                "status": st.column_config.TextColumn("Delivery Status", width="small"),
                "sent_at": st.column_config.TextColumn("Sent Timestamp", width="medium"),
                "created_at": st.column_config.TextColumn("Created Timestamp", width="medium"),
                "error_message": st.column_config.TextColumn("Error Log", width="medium"),
            },
        )
    else:
        st.info("No email outreach attempts logged yet. Click **'▶️ Execute Full Pipeline'** in the sidebar to send outreach.")
