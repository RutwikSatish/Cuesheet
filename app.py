import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="CueSheet — Production Finance",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  THEME / CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0a0a0a; color: #f5f5f1; }
  [data-testid="stSidebar"] { background: #141414; border-right: 1px solid #2a2a2a; }
  [data-testid="stSidebar"] * { color: #f5f5f1 !important; }
  .block-container { padding: 1.5rem 2rem; }
  h1, h2, h3 { color: #f5f5f1 !important; }
  .stMetric { background: #141414; border: 1px solid #2a2a2a; border-radius: 8px; padding: 12px !important; }
  .stMetric label { color: #999 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
  .stMetric [data-testid="stMetricValue"] { color: #f5f5f1 !important; font-size: 2rem !important; font-weight: 800 !important; }
  div[data-testid="stDataFrame"] { border: 1px solid #2a2a2a; border-radius: 8px; }
  .stSelectbox > div, .stMultiSelect > div { background: #1e1e1e !important; border-color: #2a2a2a !important; }
  .stButton > button { background: #e50914 !important; color: white !important; border: none !important; font-weight: 700 !important; border-radius: 5px !important; }
  .stButton > button:hover { background: #c0070f !important; }
  .stTabs [data-baseweb="tab-list"] { background: #141414; border-bottom: 1px solid #2a2a2a; gap: 4px; }
  .stTabs [data-baseweb="tab"] { background: transparent; color: #999; font-weight: 600; font-size: 13px; border-radius: 4px 4px 0 0; }
  .stTabs [aria-selected="true"] { background: #252525 !important; color: #f5f5f1 !important; border-bottom: 2px solid #e50914 !important; }
  .pill-complete { background: rgba(70,211,105,0.15); color: #46d369; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
  .pill-pending  { background: rgba(255,215,0,0.15);  color: #ffd700; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
  .pill-overdue  { background: rgba(229,9,20,0.18);   color: #e50914; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
  .kpi-card { background: #141414; border: 1px solid #2a2a2a; border-radius: 8px; padding: 16px 20px; margin-bottom: 8px; }
  .alert-critical { border-left: 3px solid #e50914; background: #141414; border: 1px solid #2a2a2a; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
  .alert-warn { border-left: 3px solid #ffd700; background: #141414; border: 1px solid #2a2a2a; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
  .alert-info { border-left: 3px solid #4da1f5; background: #141414; border: 1px solid #2a2a2a; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
  hr { border-color: #2a2a2a !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SEED DATA
# ─────────────────────────────────────────
DOCS      = ["W-4", "I-9", "Direct Deposit", "Deal Memo", "Emergency Contact"]
DEPTS     = ["Camera", "Production", "Art", "Sound", "G&E", "Wardrobe"]
PARTNERS  = ["Entertainment Partners Inc.", "Summit Payroll Services", "Crew & Cast Financial"]
STATUS_OPTIONS = ["Complete", "Pending", "Overdue", "N/A"]
STATUS_EMOJI   = {"Complete": "✅", "Pending": "⏳", "Overdue": "🔴", "N/A": "—"}

NAMES = [
    "James Whitfield","Rachel Torres","Omar Siddiqui","Tara Lennox","Devon Marsh",
    "Aisha Kumar","Ben Patel","Mia Chen","Lucas Ford","Nina Reyes","Sam Okafor","Zara Bloom",
    "Chris Vance","Diana Park","Eli Stone","Fiona Walsh","Greg Mills","Hannah Rose",
    "Ivan Cole","Julia Hart","Karl Bex","Lena Moor","Mike Sato","Nora Kim","Owen Drake",
    "Paula Webb","Quinn Nash","Rosa Diaz","Steve Lau","Tina Vu","Uma Ferris","Victor Jang",
    "Wendy Ho","Xander Fox","Yuki Tan","Zoe Reed","Aaron Miles","Bella Cruz","Carlos Wu",
    "Daisy Finn","Eddie Grant","Faye Long","Glen Addo","Hana Ito","Igor Petrov",
    "Jade Moon","Kevin Shah","Lola Burns",
]

def build_doc_status(i):
    if i < 6:   return ["Overdue", "Pending", "Overdue", "Pending", "Overdue"]
    if i < 17:  return ["Pending", "Complete", "Complete", "Pending", "Complete"]
    return ["Complete"] * 5

def overall_status(docs):
    if all(d == "Complete" for d in docs): return "Complete"
    if any(d == "Overdue"  for d in docs): return "Overdue"
    return "Pending"

def make_crew_df():
    rows = []
    for i, name in enumerate(NAMES):
        dept    = DEPTS[i % len(DEPTS)]
        partner = PARTNERS[i % len(PARTNERS)]
        docs    = build_doc_status(i)
        month   = "Mar" if i < 20 else "Apr"
        day     = 10 + (i % 18)
        rows.append({
            "Name": name, "Department": dept, "Payroll Partner": partner,
            "Start Date": f"{month} {day}, 2026",
            **{f"doc_{d}": docs[j] for j, d in enumerate(DOCS)},
            "Overall": overall_status(docs),
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────
if "crew" not in st.session_state:
    st.session_state.crew = make_crew_df()
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = [
        {"Partner": "Entertainment Partners Inc.", "Issue": "Missing I-9 — camera crew", "Crew Affected": 3, "Priority": "High",   "Status": "Open",     "Logged": "Today 9:14am"},
        {"Partner": "Summit Payroll Services",     "Issue": "Art dept deal memos not received", "Crew Affected": 7, "Priority": "High",   "Status": "Open",     "Logged": "Yesterday 4:02pm"},
        {"Partner": "Summit Payroll Services",     "Issue": "W-4 updates needed",               "Crew Affected": 5, "Priority": "Medium", "Status": "Open",     "Logged": "Yesterday 4:02pm"},
        {"Partner": "Crew & Cast Financial",       "Issue": "DD form countersignature pending",  "Crew Affected": 3, "Priority": "Low",    "Status": "Resolved", "Logged": "Today 8:45am"},
    ]

df = st.session_state.crew

# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 CueSheet")
    st.markdown("**Production Finance**")
    st.divider()
    st.markdown("**Production:** The Meridian — S01")
    st.markdown("**Week:** 14 of Production")
    st.markdown(f"**Date:** {date.today().strftime('%b %d, %Y')}")
    st.divider()

    overdue_n = len(df[df["Overall"] == "Overdue"])
    pending_n = len(df[df["Overall"] == "Pending"])
    complete_n = len(df[df["Overall"] == "Complete"])

    st.markdown(f"🔴 **{overdue_n}** Overdue")
    st.markdown(f"⏳ **{pending_n}** Pending")
    st.markdown(f"✅ **{complete_n}** Complete")
    st.divider()
    st.caption("Built by Rutwik Satish")
    st.caption("github.com/rutwik · streamlit")

# ─────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", "📋 Start Packets", "🤝 Payroll Partners", "🚨 Alerts", "📅 Calendar"
])

# ═══════════════════════════════════════════
#  TAB 1 — DASHBOARD
# ═══════════════════════════════════════════
with tab1:
    st.markdown("## Production Overview")
    st.caption("The Meridian — Season 01  ·  Updated today")
    st.divider()

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Crew",        len(df),       "6 departments")
    c2.metric("Packets Complete",  complete_n,    f"{complete_n/len(df)*100:.0f}% completion")
    c3.metric("Pending Review",    pending_n,     "Awaiting docs")
    c4.metric("Overdue",           overdue_n,     "Past 48-hr window", delta_color="inverse")

    st.divider()
    col_l, col_r = st.columns(2)

    # Dept completion bar chart
    with col_l:
        st.markdown("#### Completion by Department")
        dept_data = []
        for dept in DEPTS:
            sub = df[df["Department"] == dept]
            done = len(sub[sub["Overall"] == "Complete"])
            dept_data.append({"Department": dept, "Complete": done, "Total": len(sub), "Pct": done/len(sub)*100})
        dept_df = pd.DataFrame(dept_data)
        fig_dept = go.Figure()
        fig_dept.add_trace(go.Bar(
            x=dept_df["Pct"], y=dept_df["Department"], orientation="h",
            marker_color=["#46d369" if p >= 80 else "#ffd700" if p >= 50 else "#e50914" for p in dept_df["Pct"]],
            text=[f"{r['Complete']}/{r['Total']}" for _, r in dept_df.iterrows()],
            textposition="outside", textfont_color="#f5f5f1",
        ))
        fig_dept.update_layout(
            paper_bgcolor="#141414", plot_bgcolor="#141414", font_color="#f5f5f1",
            xaxis=dict(range=[0,115], showgrid=False, ticksuffix="%"),
            yaxis=dict(showgrid=False), margin=dict(l=10,r=30,t=10,b=10), height=260,
            showlegend=False,
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    # Doc coverage donut
    with col_r:
        st.markdown("#### Document Type Coverage")
        doc_pcts = []
        for d in DOCS:
            col = f"doc_{d}"
            pct = len(df[df[col] == "Complete"]) / len(df) * 100
            doc_pcts.append({"Doc": d, "Pct": round(pct, 1)})
        doc_df = pd.DataFrame(doc_pcts)
        fig_doc = go.Figure(go.Bar(
            x=doc_df["Doc"], y=doc_df["Pct"],
            marker_color=["#46d369" if p >= 90 else "#4da1f5" if p >= 70 else "#ffd700" if p >= 50 else "#e50914" for p in doc_df["Pct"]],
            text=[f"{p}%" for p in doc_df["Pct"]], textposition="outside", textfont_color="#f5f5f1",
        ))
        fig_doc.update_layout(
            paper_bgcolor="#141414", plot_bgcolor="#141414", font_color="#f5f5f1",
            yaxis=dict(range=[0,115], showgrid=False, ticksuffix="%"),
            xaxis=dict(showgrid=False), margin=dict(l=10,r=10,t=10,b=10), height=260,
            showlegend=False,
        )
        st.plotly_chart(fig_doc, use_container_width=True)

    # Payroll progress
    st.markdown("#### Payroll Partner Submission Status")
    p1, p2, p3 = st.columns(3)
    partner_stats = [
        ("Entertainment Partners Inc.", 82, "✅ On Track",  "#46d369"),
        ("Summit Payroll Services",     55, "⚠️ Behind",   "#ffd700"),
        ("Crew & Cast Financial",       93, "✅ On Track",  "#46d369"),
    ]
    for col, (name, pct, status, color) in zip([p1, p2, p3], partner_stats):
        with col:
            st.markdown(f"**{name}**")
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=pct,
                number={"suffix": "%", "font": {"color": color, "size": 28}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#555"},
                    "bar": {"color": color},
                    "bgcolor": "#252525", "bordercolor": "#2a2a2a",
                    "steps": [{"range": [0, pct], "color": color}],
                },
            ))
            fig_g.update_layout(
                paper_bgcolor="#141414", font_color="#f5f5f1",
                margin=dict(l=20, r=20, t=20, b=10), height=160,
            )
            st.plotly_chart(fig_g, use_container_width=True)
            st.caption(status)

# ═══════════════════════════════════════════
#  TAB 2 — START PACKETS
# ═══════════════════════════════════════════
with tab2:
    st.markdown("## Start Packet Tracker")
    st.caption("Monitor document submission status for all 48 crew members")
    st.divider()

    # Filters
    fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 3])
    with fc1:
        status_filter = st.selectbox("Status", ["All", "Overdue", "Pending", "Complete"])
    with fc2:
        dept_filter = st.selectbox("Department", ["All"] + DEPTS)
    with fc3:
        partner_filter = st.selectbox("Payroll Partner", ["All"] + PARTNERS)
    with fc4:
        search = st.text_input("Search crew member", placeholder="Type name...")

    # Apply filters
    filtered = df.copy()
    if status_filter != "All":   filtered = filtered[filtered["Overall"] == status_filter]
    if dept_filter != "All":     filtered = filtered[filtered["Department"] == dept_filter]
    if partner_filter != "All":  filtered = filtered[filtered["Payroll Partner"] == partner_filter]
    if search:                   filtered = filtered[filtered["Name"].str.lower().str.contains(search.lower())]

    st.caption(f"Showing {len(filtered)} of {len(df)} crew members")

    # Colour cells
    def style_overall(val):
        c = {"Complete": "#46d369", "Pending": "#ffd700", "Overdue": "#e50914", "N/A": "#999"}
        return f"color: {c.get(val,'#f5f5f1')}; font-weight: 700;"

    def style_doc(val):
        c = {"Complete": "color:#46d369", "Pending": "color:#ffd700", "Overdue": "color:#e50914; font-weight:700;", "N/A": "color:#555"}
        return c.get(val, "")

    display_cols = ["Name", "Department", "Payroll Partner", "Start Date"] + [f"doc_{d}" for d in DOCS] + ["Overall"]
    rename_map   = {f"doc_{d}": d for d in DOCS}
    display_df   = filtered[display_cols].rename(columns=rename_map)

    styled = display_df.style \
        .applymap(style_doc, subset=DOCS) \
        .applymap(style_overall, subset=["Overall"])

    st.dataframe(styled, use_container_width=True, height=420)

    # Action buttons
    ba1, ba2, ba3 = st.columns([2, 2, 5])
    with ba1:
        if st.button("📧 Send Reminders"):
            n = len(df[df["Overall"] == "Overdue"])
            st.success(f"✅ Automated reminders sent to {n} overdue crew members. Payroll partners CC'd.")
    with ba2:
        csv = df.to_csv(index=False)
        st.download_button("⬇ Export CSV", data=csv, file_name="CueSheet_StartPackets.csv", mime="text/csv")

    # Edit individual crew member
    st.divider()
    st.markdown("#### Edit Crew Member Status")
    crew_sel = st.selectbox("Select crew member to update", df["Name"].tolist())
    row_idx  = df[df["Name"] == crew_sel].index[0]
    row      = df.loc[row_idx]

    ecols = st.columns(len(DOCS))
    new_vals = {}
    for i, (col, doc) in enumerate(zip(ecols, DOCS)):
        with col:
            new_vals[doc] = st.selectbox(doc, STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(row[f"doc_{doc}"]), key=f"edit_{doc}_{row_idx}")

    if st.button("💾 Save Changes"):
        for doc, val in new_vals.items():
            st.session_state.crew.loc[row_idx, f"doc_{doc}"] = val
        new_overall = overall_status(list(new_vals.values()))
        st.session_state.crew.loc[row_idx, "Overall"] = new_overall
        st.success(f"✅ {crew_sel}'s packet updated. Overall status: **{new_overall}**")
        st.rerun()

# ═══════════════════════════════════════════
#  TAB 3 — PAYROLL PARTNERS
# ═══════════════════════════════════════════
with tab3:
    st.markdown("## Payroll Partner Coordination")
    st.caption("Track packet delivery, feedback, and outstanding issues per payroll partner")
    st.divider()

    partner_info = [
        {"name": "Entertainment Partners Inc.", "contact": "Sandra Ng", "email": "sandra@epi-payroll.com",
         "pct": 82, "received": 41, "status": "On Track",  "color": "#46d369",
         "feedback": "Missing I-9 for 3 camera crew — please prioritize.",
         "deadline": "Friday 5PM", "last_sync": "2 hrs ago"},
        {"name": "Summit Payroll Services", "contact": "Marcus Bell", "email": "m.bell@summitpay.com",
         "pct": 55, "received": 26, "status": "Behind Schedule", "color": "#ffd700",
         "feedback": "Art dept deal memos not yet received. W-4 updates needed for 5 crew.",
         "deadline": "Friday 5PM ⚠️ 18 hrs", "last_sync": "1 day ago"},
        {"name": "Crew & Cast Financial", "contact": "Priya Mehra", "email": "priya@ccfinancial.co",
         "pct": 93, "received": 45, "status": "On Track", "color": "#46d369",
         "feedback": "All good — minor DD form revisions for 3 crew pending countersignature.",
         "deadline": "Friday 5PM", "last_sync": "30 min ago"},
    ]

    pc1, pc2, pc3 = st.columns(3)
    for col, p in zip([pc1, pc2, pc3], partner_info):
        with col:
            st.markdown(f"**{p['name']}**")
            st.caption(f"📧 {p['contact']} · {p['email']}")
            st.caption(f"Last sync: {p['last_sync']}")
            fig_p = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=p["pct"],
                delta={"reference": 80, "valueformat": ".0f"},
                number={"suffix": "%", "font": {"color": p["color"], "size": 32}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": p["color"]},
                    "bgcolor": "#252525", "bordercolor": "#2a2a2a",
                    "threshold": {"line": {"color": "#e50914", "width": 2}, "thickness": 0.75, "value": 80},
                },
            ))
            fig_p.update_layout(
                paper_bgcolor="#141414", font_color="#f5f5f1",
                margin=dict(l=20,r=20,t=30,b=0), height=180,
            )
            st.plotly_chart(fig_p, use_container_width=True)
            st.caption(f"📦 {p['received']}/48 packets · Deadline: {p['deadline']}")
            st.markdown(f"*\"{p['feedback']}\"*")
            st.markdown("---")

    # Feedback log
    st.markdown("#### Outstanding Feedback Log")
    fb_df = pd.DataFrame(st.session_state.feedback_log)

    def style_priority(val):
        return {"High": "color:#e50914;font-weight:700;", "Medium": "color:#ffd700;font-weight:700;", "Low": "color:#46d369;"}.get(val, "")
    def style_status(val):
        return "color:#46d369;" if val == "Resolved" else "color:#ffd700;"

    styled_fb = fb_df.style.applymap(style_priority, subset=["Priority"]).applymap(style_status, subset=["Status"])
    st.dataframe(styled_fb, use_container_width=True)

    # Add new feedback
    with st.expander("➕ Log New Payroll Feedback"):
        nf1, nf2 = st.columns(2)
        with nf1:
            new_partner  = st.selectbox("Partner", PARTNERS, key="new_partner")
            new_issue    = st.text_input("Issue Description", key="new_issue")
        with nf2:
            new_affected = st.number_input("Crew Affected", 1, 48, 1, key="new_affected")
            new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="new_priority")
        if st.button("Log Feedback"):
            st.session_state.feedback_log.append({
                "Partner": new_partner, "Issue": new_issue,
                "Crew Affected": new_affected, "Priority": new_priority,
                "Status": "Open", "Logged": "Just now",
            })
            st.success("✅ Feedback logged.")
            st.rerun()

# ═══════════════════════════════════════════
#  TAB 4 — ALERTS
# ═══════════════════════════════════════════
with tab4:
    st.markdown("## Alerts & Reminders")
    st.caption("Automated flags for missing documents, overdue packets, and deadline risks")
    st.divider()

    alerts = [
        {"level": "critical", "icon": "🚨", "title": f"{overdue_n} Crew Members Have Overdue Start Packets",
         "desc": "James W., Tara L., Devon M., Aisha K., Ben P., Mia C. — past 48-hour submission window. Summit Payroll deadline in 18 hours. Immediate follow-up required.",
         "time": "18 hrs remaining", "action": "Send Reminder"},
        {"level": "critical", "icon": "⚠️", "title": "Summit Payroll Partner — Packet Submission at 55%",
         "desc": "Summit Payroll requires all start packets by Friday 5PM. Currently at 55% (26/48). At current pace, 10+ packets will miss the deadline. Escalation recommended.",
         "time": "Today", "action": "Escalate"},
        {"level": "warn", "icon": "📄", "title": "I-9 Missing for 3 Camera Department Crew",
         "desc": "Entertainment Partners Inc. flagged missing I-9 forms for: James W., Rachel T., Omar S. Must be submitted before first day of principal photography per compliance requirements.",
         "time": "2 hrs ago", "action": "View Crew"},
        {"level": "warn", "icon": "📝", "title": "7 Art Department Deal Memos Not Received by Payroll",
         "desc": "Summit Payroll confirmed they have not received deal memos for the full Art Department. Memos may have been signed but not uploaded to the shared folder. Please verify and re-upload.",
         "time": "Yesterday", "action": "View Docs"},
        {"level": "info", "icon": "📅", "title": "Weekly Payroll Sync — Tomorrow 10AM",
         "desc": "Scheduled check-in with all 3 payroll partners. Prepare: (1) updated submission summary, (2) list of outstanding issues, (3) revised ETA for overdue packets.",
         "time": "Tomorrow", "action": "View Report"},
        {"level": "info", "icon": "✅", "title": "Crew & Cast Financial — 93% Submission Rate Achieved",
         "desc": "Crew & Cast Financial acknowledged receipt of 45/48 packets. Remaining 3 (DD form revisions) expected by EOD. No escalation needed.",
         "time": "30 min ago", "action": None},
    ]

    level_color = {"critical": "#e50914", "warn": "#ffd700", "info": "#4da1f5"}
    for a in alerts:
        color = level_color[a["level"]]
        with st.container():
            ac1, ac2 = st.columns([10, 2])
            with ac1:
                st.markdown(f"""
                <div style="border-left:3px solid {color};background:#141414;border:1px solid #2a2a2a;
                            border-radius:8px;padding:14px 16px;margin-bottom:10px;">
                  <div style="font-weight:800;font-size:13px;margin-bottom:4px;">{a['icon']} {a['title']}</div>
                  <div style="font-size:11px;color:#999;line-height:1.5;">{a['desc']}</div>
                  <div style="font-size:10px;color:#666;margin-top:6px;">{a['time']}</div>
                </div>""", unsafe_allow_html=True)
            with ac2:
                if a["action"]:
                    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                    st.button(a["action"], key=f"alert_{a['title'][:20]}")

# ═══════════════════════════════════════════
#  TAB 5 — CALENDAR
# ═══════════════════════════════════════════
with tab5:
    st.markdown("## Production Finance Calendar")
    st.caption("Payroll deadlines, team syncs, and key deliverables — Week of Mar 30, 2026")
    st.divider()

    events = [
        {"day": "Mon Mar 30", "time": "9:00 AM",  "title": "Weekly Production Finance Standup",           "attendees": "Production Finance Team",             "type": "Internal",        "color": "#46d369"},
        {"day": "Mon Mar 30", "time": "2:00 PM",  "title": "Start Packet Review — Camera Dept",            "attendees": "Dept Coordinator, Sandra Ng (EPI)",    "type": "Payroll Partner", "color": "#4da1f5"},
        {"day": "Tue Mar 31", "time": "10:00 AM", "title": "Summit Payroll Escalation Call",               "attendees": "Marcus Bell (Summit), Finance Lead",   "type": "Payroll Partner", "color": "#ffd700"},
        {"day": "Wed Apr 1",  "time": "11:00 AM", "title": "Internal Audit — Packet Compliance Check",     "attendees": "Internal Audit, Risk Assurance",       "type": "Internal",        "color": "#46d369"},
        {"day": "Thu Apr 2",  "time": "3:00 PM",  "title": "Crew & Cast Financial Weekly Sync",            "attendees": "Priya Mehra (CCF), Coordinator",       "type": "Payroll Partner", "color": "#4da1f5"},
        {"day": "Fri Apr 3",  "time": "5:00 PM",  "title": "⚠ ALL Start Packets Due — Summit Payroll",    "attendees": "Hard deadline — 48 packets required",  "type": "Hard Deadline",   "color": "#e50914"},
        {"day": "Fri Apr 3",  "time": "11:00 AM", "title": "Weekly Status Digest — Auto-Send",             "attendees": "All Production Finance stakeholders",  "type": "Auto Report",     "color": "#46d369"},
        {"day": "Recurring",  "time": "Every Mon", "title": "Business Update Broadcast to Finance Team",   "attendees": "Full Production Finance Team",         "type": "Internal",        "color": "#46d369"},
        {"day": "Recurring",  "time": "Every Fri", "title": "Payroll Partner Feedback Consolidation",      "attendees": "Coordinator + all 3 partners",         "type": "Payroll Partner", "color": "#4da1f5"},
    ]

    cols_cal = st.columns(3)
    for i, ev in enumerate(events):
        with cols_cal[i % 3]:
            st.markdown(f"""
            <div style="background:#141414;border:1px solid {'#e50914' if ev['type']=='Hard Deadline' else '#2a2a2a'};
                        border-radius:8px;padding:14px 16px;margin-bottom:12px;">
              <div style="font-size:10px;color:#999;margin-bottom:4px;">{ev['day']} · {ev['time']}</div>
              <div style="font-weight:800;font-size:12px;margin-bottom:4px;">{ev['title']}</div>
              <div style="font-size:11px;color:#999;">{ev['attendees']}</div>
              <div style="display:inline-block;background:rgba(255,255,255,0.07);color:{ev['color']};
                          padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;margin-top:6px;">
                {ev['type']}
              </div>
            </div>""", unsafe_allow_html=True)

    # Add event
    with st.expander("➕ Add Calendar Event"):
        ce1, ce2 = st.columns(2)
        with ce1:
            ev_title = st.text_input("Event Title")
            ev_date  = st.date_input("Date", value=date.today())
        with ce2:
            ev_attendees = st.text_input("Attendees")
            ev_type = st.selectbox("Type", ["Internal", "Payroll Partner", "Hard Deadline", "Auto Report"])
        if st.button("Add Event"):
            st.success(f"✅ '{ev_title}' added to calendar for {ev_date.strftime('%b %d, %Y')}.")
