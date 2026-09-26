"""
Automated Micro-Influencer Outreach System
Clean, Premium & Intuitive Dashboard
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
import re
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DB_PATH, TARGET_NICHE, MIN_FOLLOWERS, MAX_FOLLOWERS, MIN_ENGAGEMENT_RATE, SMTP_EMAIL
from src.database.models import (
    get_stats,
    get_all_influencers,
    get_qualified_influencers,
    get_outreach_logs,
    clear_all_data,
    delete_influencer,
    clear_influencer_message,
    update_influencer,
)
from src.pipeline import OutreachPipeline
from src.outreach.tracker import OutreachTracker
from src.outreach.email_sender import EmailSender
from src.personalization.generator import MessageGenerator

# -----------------------------------------------------------------------------
# 1. Page Configuration & Premium Minimalist CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Influencer Outreach Studio",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&display=swap');

    /* Global Typography & Text Colors */
    html, body, p, label, h1, h2, h3, h4, h5, h6, .stMarkdown, [data-testid="stMarkdownContainer"] p {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0F2942;
    }
    
    /* Preserve Streamlit Material Icons */
    [data-testid="stSidebarCollapseButton"] span, 
    [data-testid="stIcon"], 
    i, 
    .material-symbols-outlined, 
    .material-icons {
        font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Icons' !important;
        font-weight: normal !important;
    }

    /* Light Blue & Pure White Background */
    .stApp {
        background: linear-gradient(180deg, #F0F7FF 0%, #FFFFFF 320px, #F4F9FD 100%);
        background-attachment: fixed;
    }

    .main .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
    }

    /* Sidebar Styling - Light Blue Palette */
    section[data-testid="stSidebar"] {
        background-color: #F8FBFF !important;
        border-right: 1px solid #BAE6FD !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #0369A1 !important;
    }
    section[data-testid="stSidebar"] .stCaption {
        color: #0284C7 !important;
    }

    /* Premium White & Light Blue Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #E0F2FE 0%, #EFF6FF 50%, #FFFFFF 100%);
        border: 1px solid #BAE6FD;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px -2px rgba(14, 165, 233, 0.12);
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0369A1 !important;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 0.92rem;
        color: #0284C7 !important;
        font-weight: 600;
        margin-top: 0.25rem;
    }
    .hero-tag {
        background: #FFFFFF;
        color: #0284C7 !important;
        border: 1px solid #7DD3FC;
        padding: 0.4rem 0.95rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.12);
    }

    /* Modern Minimalist KPI Cards - White & Light Blue */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E0F2FE;
        border-top: 3.5px solid #0EA5E9;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 2px 10px rgba(14, 165, 233, 0.05);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #7DD3FC;
        box-shadow: 0 8px 24px rgba(14, 165, 233, 0.15);
    }
    .kpi-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0369A1 !important;
        line-height: 1.1;
    }
    .kpi-lbl {
        font-size: 0.78rem;
        font-weight: 700;
        color: #0284C7 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 0.35rem;
    }

    /* Pill Badges */
    .pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .pill-blue {
        background: #E0F2FE;
        color: #0284C7 !important;
        border: 1px solid #BAE6FD;
    }
    .pill-green {
        background: #F0FDF4;
        color: #059669 !important;
        border: 1px solid #A7F3D0;
    }
    .pill-red {
        background: #FEF2F2;
        color: #E11D48 !important;
        border: 1px solid #FECDD3;
    }
    .pill-amber {
        background: #F0F9FF;
        color: #0284C7 !important;
        border: 1px solid #BAE6FD;
    }

    /* Modern Tabs in White & Light Blue */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E0F2FE;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #BAE6FD;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        color: #0369A1 !important;
        font-weight: 700 !important;
        font-size: 0.9rem;
        padding: 0 16px;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.6);
        color: #0284C7 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #0284C7 !important;
        font-weight: 800 !important;
        border: 1px solid #BAE6FD;
        box-shadow: 0 2px 10px rgba(14, 165, 233, 0.15);
    }

    /* Clean Card Container */
    .clean-box {
        background: #FFFFFF;
        border: 1px solid #BAE6FD;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.05);
    }

    /* Rule Badges */
    .rule-badge {
        background: #FFFFFF;
        border: 1px solid #BAE6FD;
        border-top: 3px solid #38BDF8;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        text-align: center;
        box-shadow: 0 2px 6px rgba(14, 165, 233, 0.05);
    }
    .rule-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #0284C7;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .rule-val {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0369A1;
    }

    /* Buttons Styling in White & Light Blue */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        border: 1px solid #BAE6FD;
        background: #FFFFFF;
        color: #0284C7;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #F0F9FF;
        border-color: #38BDF8;
        color: #0369A1;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0284C7 0%, #0EA5E9 100%) !important;
        border: 1px solid #0284C7 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369A1 0%, #0284C7 100%) !important;
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.35) !important;
    }

    /* Inputs, Textareas, Selectboxes */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #BAE6FD !important;
        border-radius: 8px !important;
        color: #0F172A !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0EA5E9 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
    }

    /* Dataframe container */
    [data-testid="stDataFrame"] {
        border: 1px solid #BAE6FD !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        background: #FFFFFF !important;
    }

    /* Streamlit Radios & Checkboxes */
    .stRadio [role="radiogroup"] {
        background-color: #F0F9FF;
        padding: 6px 12px;
        border-radius: 10px;
        border: 1px solid #BAE6FD;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Data Loaders
# -----------------------------------------------------------------------------
def load_data():
    """Load latest dataset from SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    df_all = pd.read_sql_query("SELECT * FROM influencers ORDER BY followers DESC", conn)
    df_logs = pd.read_sql_query("""
        SELECT ol.id, i.name, i.platform, i.email, ol.channel, ol.status, ol.sent_at, ol.created_at, ol.error_message
        FROM outreach_log ol
        JOIN influencers i ON ol.influencer_id = i.id
        ORDER BY ol.id DESC
    """, conn)
    conn.close()
    return df_all, df_logs


# -----------------------------------------------------------------------------
# 3. Sidebar Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Quick Controls")
    st.caption(f"Niche: **{TARGET_NICHE}** | Rules: **5K–100K Subs**")
    st.divider()

    if st.button("Run Full Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Executing pipeline..."):
            pipeline = OutreachPipeline(simulate_email=True)
            res = pipeline.run_full_pipeline()
            if res.get("success"):
                st.toast("Pipeline complete! Creators discovered and qualified.")
                st.rerun()
            else:
                st.error(f"Error: {res.get('error')}")

    if st.button("Load 50 Demo Creators", use_container_width=True):
        with st.spinner("Loading demo records..."):
            import subprocess
            subprocess.run([sys.executable, "run.py", "--action", "demo-data"], cwd=str(PROJECT_ROOT))
            st.toast("50 Demo creators loaded and qualified.")
            st.rerun()

    if st.button("Export CSV Reports", use_container_width=True):
        tracker = OutreachTracker()
        tracker.export_all()
        st.toast("CSV files saved to data/ and outputs/.")

    if st.button("Clear Database", use_container_width=True):
        clear_all_data()
        st.toast("Database reset successfully.")
        st.rerun()

    st.divider()
    st.caption("AI Outreach Pipeline • Safe Mode Active")


# -----------------------------------------------------------------------------
# 4. Header Banner & KPIs
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div>
        <div class="hero-title">AI Micro-Influencer Outreach Studio</div>
        <div class="hero-subtitle">Discovery • Qualification Audit • AI Personalization • User-Approved Delivery</div>
    </div>
    <div class="hero-tag">Live Studio</div>
</div>
""", unsafe_allow_html=True)

df_all, df_logs = load_data()
stats = get_stats()

# KPI Metric Row
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-val" style="color: #0369A1 !important;">{stats['total_discovered']}</div>
        <div class="kpi-lbl">Total Discovered</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-val" style="color: #0284C7 !important;">{stats['qualified']}</div>
        <div class="kpi-lbl">Qualified (5K–100K)</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-val" style="color: #E11D48 !important;">{stats['disqualified']}</div>
        <div class="kpi-lbl">Filtered Out</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-val" style="color: #0284C7 !important;">{stats['messages_generated']}</div>
        <div class="kpi-lbl">AI Pitches Ready</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-val" style="color: #0EA5E9 !important;">{stats['emails_sent']}</div>
        <div class="kpi-lbl">Emails Sent</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. Tab Navigation
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Pipeline Overview",
    "Discovered Creators",
    "Qualification Audit",
    "AI Email Studio",
    "Delivery Logs",
])


# -----------------------------------------------------------------------------
# TAB 1: Pipeline Overview
# -----------------------------------------------------------------------------
with tab1:
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("##### Qualification Breakdown")
        if stats["total_discovered"] > 0:
            status_df = pd.DataFrame({
                "Category": ["Qualified", "Disqualified", "Pending"],
                "Creators": [stats["qualified"], stats["disqualified"], stats["pending_qualification"]],
            }).set_index("Category")
            st.bar_chart(status_df, color="#0EA5E9", height=240)
        else:
            st.info("No data yet. Click **'Load 50 Demo Creators'** in the sidebar.")

    with c_right:
        st.markdown("##### Top Creators by Audience Size")
        if not df_all.empty and "followers" in df_all.columns:
            top_df = df_all.head(8)[["name", "followers"]].set_index("name")
            st.bar_chart(top_df, color="#38BDF8", height=240)
        else:
            st.info("No follower metrics available.")

    st.markdown("##### End-to-End Pipeline Workflow")
    st.dataframe(
        pd.DataFrame([
            {"Stage": "1. Discovery", "Engine": "YouTube API & Scraper", "Criteria": f"Niche: {TARGET_NICHE}", "Output": f"{stats['total_discovered']} Discovered"},
            {"Stage": "2. Qualification", "Engine": "Quantitative Rules", "Criteria": "5K–100K Subs, ≥2% Eng Rate", "Output": f"{stats['qualified']} Qualified"},
            {"Stage": "3. Enrichment", "Engine": "Contact & Profile Parser", "Criteria": "Extract verified business emails", "Output": f"{stats['total_discovered']} Enriched"},
            {"Stage": "4. AI Pitch", "Engine": "Groq / Gemini LLM", "Criteria": "Custom 60–90w Email + 15–30w DM", "Output": f"{stats['messages_generated']} Pitches"},
            {"Stage": "5. Outreach", "Engine": "SMTP / Safe Simulator", "Criteria": "Duplicate prevention & audit log", "Output": f"{stats['emails_sent']} Delivered"},
        ]),
        use_container_width=True,
        hide_index=True,
    )


# -----------------------------------------------------------------------------
# TAB 2: Discovered Creators
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("##### Influencer Database")
    
    col_s, col_f, col_d = st.columns([3, 2, 2])
    with col_s:
        search = st.text_input("Search:", "", placeholder="Search by name, email, or theme...", label_visibility="collapsed")
    with col_f:
        filter_st = st.selectbox("Status:", ["QUALIFIED (5K–100K)", "All Records", "DISQUALIFIED"], label_visibility="collapsed")

    filtered_df = df_all.copy()
    if "QUALIFIED" in filter_st:
        filtered_df = filtered_df[filtered_df["qualification_status"] == "QUALIFIED"]
    elif "DISQUALIFIED" in filter_st:
        filtered_df = filtered_df[filtered_df["qualification_status"] == "DISQUALIFIED"]

    if search:
        s_low = search.lower()
        filtered_df = filtered_df[
            filtered_df["name"].str.lower().str.contains(s_low, na=False) |
            filtered_df["email"].str.lower().str.contains(s_low, na=False) |
            filtered_df["content_themes"].str.lower().str.contains(s_low, na=False)
        ]

    cols_show = ["name", "platform", "followers", "engagement_rate", "niche", "content_themes", "email", "qualification_status", "outreach_status"]
    avail = [c for c in cols_show if c in filtered_df.columns]

    st.dataframe(
        filtered_df[avail],
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "name": st.column_config.TextColumn("Creator", width="medium"),
            "platform": st.column_config.TextColumn("Platform", width="small"),
            "followers": st.column_config.NumberColumn("Subs / Followers", format="%d"),
            "engagement_rate": st.column_config.NumberColumn("Eng. Rate", format="%.2f%%"),
            "niche": st.column_config.TextColumn("Niche", width="small"),
            "content_themes": st.column_config.TextColumn("Themes", width="medium"),
            "email": st.column_config.TextColumn("Email", width="medium"),
            "qualification_status": st.column_config.TextColumn("Verdict", width="small"),
            "outreach_status": st.column_config.TextColumn("Outreach", width="small"),
        },
    )

    # Clean Delete Option
    with st.expander("Delete Channel Record", expanded=False):
        if not df_all.empty:
            d_c1, d_c2 = st.columns([3, 1])
            with d_c1:
                del_name = st.selectbox("Select channel to remove:", df_all["name"].tolist(), key="tab2_del_name")
            with d_c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Delete Channel", use_container_width=True, key="tab2_del_btn"):
                    r_del = df_all[df_all["name"] == del_name].iloc[0]
                    if delete_influencer(int(r_del["id"])):
                        st.toast(f"Deleted '{del_name}' from database.")
                        st.rerun()


# -----------------------------------------------------------------------------
# TAB 3: Qualification Audit
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("##### Multi-Rule Qualification Engine")

    # 4 Crisp Metric Badges
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown("""
        <div class="rule-badge">
            <div class="rule-label">Rule 1: Followers</div>
            <div class="rule-val">5,000 – 100,000</div>
        </div>
        """, unsafe_allow_html=True)
    with q2:
        st.markdown("""
        <div class="rule-badge">
            <div class="rule-label">Rule 2: Engagement</div>
            <div class="rule-val">≥ 2.0%</div>
        </div>
        """, unsafe_allow_html=True)
    with q3:
        st.markdown("""
        <div class="rule-badge">
            <div class="rule-label">Rule 3: Tech Relevance</div>
            <div class="rule-val">AI / ML Keywords</div>
        </div>
        """, unsafe_allow_html=True)
    with q4:
        st.markdown("""
        <div class="rule-badge">
            <div class="rule-label">Rule 4: Contact</div>
            <div class="rule-val">Valid Business Email</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    if not df_all.empty:
        sel_creator = st.selectbox("Select Creator to Inspect Decision Log:", df_all["name"].tolist())
        rec = df_all[df_all["name"] == sel_creator].iloc[0]

        a1, a2 = st.columns(2)
        with a1:
            st.markdown(f"**Creator:** `{rec['name']}` ({rec['platform']})")
            st.markdown(f"**Followers:** `{rec['followers']:,}` | **Engagement:** `{rec['engagement_rate']}%`")
            st.markdown(f"**Email:** `{rec['email']}`")
            st.markdown(f"**Themes:** `{rec['content_themes']}`")

        with a2:
            is_qual = rec.get("qualification_status") == "QUALIFIED"
            if is_qual:
                st.markdown('<span class="pill pill-green">QUALIFIED FOR OUTREACH</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pill pill-red">DISQUALIFIED</span>', unsafe_allow_html=True)

            st.code(rec.get("qualification_reason", "No audit details."), language="text")


# -----------------------------------------------------------------------------
# TAB 4: AI Email Studio & Direct Send
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("##### AI Email Outreach & Message Studio")

    if df_all.empty:
        st.info("No creators found. Load demo data or run discovery.")
    else:
        studio_view = st.radio("Workspace Mode:", ["Single Creator Email Editor", "Batch Send to All (Respective AI Pitches)"], horizontal=True)
        st.divider()

        if "Single" in studio_view:
            status_filter = st.radio(
                "Filter Creators:",
                ["Pending Outreach Only (Needs Email)", "Already Contacted / Sent", "All Qualified Creators"],
                horizontal=True,
                key="studio_status_filter"
            )

            if "Pending" in status_filter:
                pool = df_all[(df_all["qualification_status"] == "QUALIFIED") & (df_all["outreach_status"] != "SENT")]
            elif "Already" in status_filter:
                pool = df_all[(df_all["qualification_status"] == "QUALIFIED") & (df_all["outreach_status"] == "SENT")]
            else:
                pool = df_all[df_all["qualification_status"] == "QUALIFIED"]

            if pool.empty:
                if "Pending" in status_filter:
                    st.success("All qualified creators have already been emailed! Switch filter to 'Already Contacted' to inspect sent pitches.")
                else:
                    st.info("No creators match the selected filter.")
                st.stop()

            # Format options with status
            creator_options = {
                f"{r_item['name']} ({r_item.get('followers', 0):,} subs) — {'SENT' if r_item.get('outreach_status') == 'SENT' else 'PENDING'}": r_item["name"]
                for _, r_item in pool.iterrows()
            }

            sel_label = st.selectbox("Select Creator:", list(creator_options.keys()), key="studio_single_sel")
            target_name = creator_options[sel_label]
            row = pool[pool["name"] == target_name].iloc[0]
            cid = int(row["id"])
            is_already_sent = (row.get("outreach_status") == "SENT")

            # Info Header
            ih1, ih2, ih3, ih4 = st.columns(4)
            with ih1:
                st.caption("Audience")
                st.markdown(f"**{row.get('followers', 0):,} Subs**")
            with ih2:
                st.caption("Engagement")
                st.markdown(f"**{row.get('engagement_rate', 0.0)}%**")
            with ih3:
                st.caption("Contact Email")
                st.markdown(f"**{row.get('email') or 'Not Found'}**")
            with ih4:
                st.caption("Outreach Status")
                if is_already_sent:
                    st.markdown('<span class="pill pill-green">SENT</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pill pill-amber">PENDING</span>', unsafe_allow_html=True)

            if is_already_sent:
                st.info(f"Email Delivered: This creator has already been sent an outreach email. The Send button is locked to prevent duplicate emails.")

            # Parse Email Subject & Body
            raw_e = row.get("email_message") or ""
            subj_val = f"Collaboration Opportunity with {row.get('name', 'Creator')}"
            body_val = ""

            if raw_e:
                m_sub = re.search(r'Subject:\s*(.+?)(?:\n|$)', raw_e, re.IGNORECASE)
                if m_sub:
                    subj_val = m_sub.group(1).strip()
                    body_val = raw_e[m_sub.end():].strip()
                else:
                    body_val = raw_e.strip()
            else:
                body_val = (
                    f"Hi {row.get('name', 'Creator').split()[0]},\n\n"
                    f"I've been following your {row.get('content_themes', 'tech')} content and really appreciate your videos. "
                    f"Your audience aligns well with our upcoming campaign.\n\n"
                    f"We'd love to explore a sponsorship collaboration with you. Are you open to discussing details?\n\n"
                    f"Best regards,\nOutreach Team"
                )

            ed_col1, ed_col2 = st.columns([3, 2])

            with ed_col1:
                st.markdown("###### Editable Email Draft")
                to_email = st.text_input("Recipient Email:", value=row.get("email") or "", key=f"to_{cid}")
                sub_input = st.text_input("Subject Line:", value=subj_val, key=f"sub_{cid}")
                body_input = st.text_area("Email Body:", value=body_val, height=200, key=f"body_{cid}")

                mode_opt = st.radio("Delivery Mode:", ["Safe Simulation (Demo Mode)", "Real SMTP Delivery"], horizontal=True, key=f"mode_{cid}")

                b1, b2, b3, b4 = st.columns(4)

                with b1:
                    if is_already_sent:
                        if st.button("Reset & Re-send", use_container_width=True, key=f"reset_{cid}"):
                            update_influencer(cid, {"outreach_status": "PENDING", "sent_at": None})
                            st.toast(f"Status reset to Pending for {row.get('name')}.")
                            st.rerun()
                    else:
                        if st.button("Send Email", type="primary", use_container_width=True, key=f"snd_{cid}"):
                            if not to_email or "@" not in to_email or to_email == "Not Found":
                                st.error("Please specify a valid email address.")
                            else:
                                pitch_text = f"Subject: {sub_input}\n\n{body_input}"
                                update_influencer(cid, {"email": to_email, "email_message": pitch_text})

                                sim = "Simulation" in mode_opt
                                sender = EmailSender(simulate=sim)
                                res = sender.send_email({"id": cid, "name": row.get("name"), "email": to_email, "email_message": pitch_text})

                                if res.get("status") == "SENT":
                                    st.toast(f"Email sent to {to_email} successfully.")
                                    st.success(f"Email sent to **{to_email}**.")
                                    st.rerun()
                                elif res.get("status") == "DUPLICATE":
                                    st.toast("Already contacted.")
                                    st.warning("This creator was already contacted.")
                                else:
                                    st.error(f"Failed: {res.get('message')}")

                with b2:
                    if st.button("Save Draft", use_container_width=True, key=f"sav_{cid}"):
                        pitch_text = f"Subject: {sub_input}\n\n{body_input}"
                        update_influencer(cid, {"email": to_email, "email_message": pitch_text})
                        st.toast(f"Draft saved for {row.get('name')}.")
                        st.success("Draft saved to database.")

                with b3:
                    if st.button("AI Pitch", use_container_width=True, key=f"reg_{cid}"):
                        with st.spinner("Generating fresh AI pitch..."):
                            gen = MessageGenerator()
                            new_m = gen.generate_messages(dict(row))
                            update_influencer(cid, {
                                "email_message": new_m["email_message"],
                                "instagram_dm": new_m["instagram_dm"],
                                "message_generated": 1,
                            })
                            st.toast(f"Fresh AI pitch created for {row.get('name')}.")
                            st.rerun()

                with b4:
                    if st.button("Delete", use_container_width=True, key=f"del_{cid}"):
                        if delete_influencer(cid):
                            st.toast(f"Deleted {target_name}.")
                            st.rerun()

            with ed_col2:
                st.markdown("###### Instagram DM Pitch")
                st.text_area("DM Text:", value=row.get("instagram_dm") or f"Hi {row.get('name', 'Creator').split()[0]}! Love your {row.get('content_themes', 'tech')} content. Open to collaborating?", height=90, key=f"dm_{cid}")
                st.caption("Demographic & Personalization Context:")
                st.markdown(f"- **Niche:** `{row.get('niche')}`")
                st.markdown(f"- **Themes:** `{row.get('content_themes')}`")
                st.markdown(f"- **Recent Topic:** `{str(row.get('recent_content'))[:100]}...`")

        else:
            # Batch Send Console
            st.markdown("###### Batch Outreach to All Creators")
            st.caption("Sends each creator their own individually generated AI pitch to their verified email.")

            b_pool = df_all[
                (df_all["qualification_status"] == "QUALIFIED") &
                (df_all["email"].notna()) &
                (df_all["email"] != "") &
                (df_all["email"] != "Not Found")
            ]

            p_cnt = len(b_pool[b_pool["outreach_status"] == "PENDING"]) if not b_pool.empty else 0
            s_cnt = len(b_pool[b_pool["outreach_status"] == "SENT"]) if not b_pool.empty else 0

            st.markdown(f"**Eligible Creators:** `{len(b_pool)}` | **Pending Outreach:** `{p_cnt}` | **Already Sent:** `{s_cnt}`")

            b_mode = st.radio("Batch Mode:", ["Safe Simulation (Demo Mode)", "Real SMTP Delivery"], horizontal=True, key="batch_mode_sel")
            b_confirm = st.checkbox(f"I confirm sending individual AI emails to {p_cnt} pending creators.", value=False)

            if st.button("Launch Batch Outreach", type="primary", use_container_width=True, disabled=not b_confirm):
                if p_cnt == 0:
                    st.toast("No pending creators to email.")
                    st.warning("All eligible creators have already been emailed.")
                else:
                    sim = "Simulation" in b_mode
                    sender = EmailSender(simulate=sim)
                    pbar = st.progress(0, text="Starting batch outreach...")

                    targets = b_pool[b_pool["outreach_status"] == "PENDING"].to_dict("records")
                    sent_total = 0

                    for i, creator in enumerate(targets):
                        cname = creator.get("name", "Creator")
                        pbar.progress(int(((i + 1) / len(targets)) * 100), text=f"Sending ({i+1}/{len(targets)}): {cname}")

                        if not creator.get("email_message"):
                            gen = MessageGenerator()
                            m = gen.generate_messages(creator)
                            creator["email_message"] = m["email_message"]
                            creator["instagram_dm"] = m["instagram_dm"]
                            creator["message_generated"] = 1
                            update_influencer(creator["id"], m)

                        res = sender.send_email(creator)
                        if res.get("status") == "SENT":
                            sent_total += 1

                    pbar.progress(100, text="Complete!")
                    st.toast(f"Batch Outreach Done: {sent_total} emails processed.")
                    st.success(f"Successfully processed {sent_total} outreach emails.")
                    st.rerun()


# -----------------------------------------------------------------------------
# TAB 5: Delivery Logs
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("##### Outreach Delivery Audit Logs")

    if not df_logs.empty:
        st.dataframe(
            df_logs,
            use_container_width=True,
            hide_index=True,
            height=450,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Recipient", width="medium"),
                "platform": st.column_config.TextColumn("Platform", width="small"),
                "email": st.column_config.TextColumn("Email", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "sent_at": st.column_config.TextColumn("Sent Timestamp", width="medium"),
                "error_message": st.column_config.TextColumn("Details / Error", width="medium"),
            },
        )
    else:
        st.info("No delivery logs yet. Use Tab 4 to send emails.")
