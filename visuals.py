import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import ast

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="WUZZUF Market Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2a2d3e;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3a3f5c;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card .value { font-size: 2.2rem; font-weight: 700; color: #7c8cf8; }
    .metric-card .label { font-size: 0.85rem; color: #888; margin-top: 4px; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #c5c9e0;
        border-left: 3px solid #7c8cf8;
        padding-left: 10px; margin: 20px 0 12px 0;
    }
    .skill-tag-match {
        display: inline-block; background: #1a3a2a; color: #4ade80;
        border: 1px solid #22c55e; border-radius: 20px;
        padding: 3px 12px; margin: 3px; font-size: 0.82rem; font-weight: 500;
    }
    .skill-tag-missing {
        display: inline-block; background: #3a1a1a; color: #f87171;
        border: 1px solid #ef4444; border-radius: 20px;
        padding: 3px 12px; margin: 3px; font-size: 0.82rem; font-weight: 500;
    }
    .skill-tag-neutral {
        display: inline-block; background: #1e2130; color: #94a3b8;
        border: 1px solid #3a3f5c; border-radius: 20px;
        padding: 3px 12px; margin: 3px; font-size: 0.82rem;
    }
    .skill-tag-priority {
        display: inline-block; background: #2d1f3a; color: #c084fc;
        border: 1px solid #a855f7; border-radius: 20px;
        padding: 3px 12px; margin: 3px; font-size: 0.82rem; font-weight: 500;
    }
    .gap-bar-container {
        background: #1e2130; border-radius: 10px;
        height: 14px; width: 100%; margin: 8px 0; overflow: hidden;
    }
    .gap-bar-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, #7c8cf8, #a78bfa); }
    .page-title { font-size: 1.8rem; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
    .page-subtitle { font-size: 0.9rem; color: #64748b; margin-bottom: 24px; }
    .insight-card {
        background: #1e2130; border: 1px solid #3a3f5c; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 10px;
    }
    .insight-card .insight-icon { font-size: 1.4rem; margin-bottom: 4px; }
    .insight-card .insight-text { color: #c5c9e0; font-size: 0.88rem; line-height: 1.5; }
    .insight-card .insight-highlight { color: #7c8cf8; font-weight: 600; }
    .job-card {
        background: #1e2130; border: 1px solid #3a3f5c; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 8px;
    }
    .job-card .job-title { color: #e2e8f0; font-weight: 600; font-size: 0.95rem; }
    .job-card .job-meta { color: #64748b; font-size: 0.8rem; margin-top: 4px; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    p, li { color: #94a3b8; }
    label { color: #c5c9e0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
NOISE_SKILLS = {
    "information technology (it)", "computer science", "computer engineering",
    "information technology", "it", "cs", "engineering",
}

@st.cache_data
def load_data():
    df = pd.read_csv("Data/Clean/Dim_reduced_clean_data.csv")

    def parse_skills(s):
        if pd.isna(s):
            return []
        try:
            skills = ast.literal_eval(s)
            return [sk.strip().lower() for sk in skills if sk.strip().lower() not in NOISE_SKILLS]
        except:
            return []

    df["skills_list"] = df["all_skills"].apply(parse_skills)
    df["sal_mid_egp"] = (df["sal_min_egp"].fillna(0) + df["sal_max_egp"].fillna(0)) / 2
    df["career_level_short"] = df["career_level"].str.extract(r"^([^(]+)").iloc[:, 0].str.strip()
    return df

df = load_data()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#1e2130", plot_bgcolor="#1e2130",
    font=dict(color="#94a3b8", family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#7c8cf8", "#a78bfa", "#60a5fa", "#34d399", "#fb923c", "#f472b6"],
)

def metric_card(value, label):
    return f"""<div class="metric-card">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>"""

def get_top_skills(df_filtered, n=20):
    all_s = [s for sl in df_filtered["skills_list"] for s in sl]
    return Counter(all_s).most_common(n)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## WUZZUF Intelligence")
    st.markdown("<p style='color:#64748b;font-size:0.8rem;'>Egypt Job Market Analytics</p>", unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate",
        ["Market Overview", "Skill Gap Analyzer", "Skill Search",
         "Salary Intelligence", "Company Explorer", "Career Path Planner"],
        label_visibility="collapsed",
    )

    st.divider()

    # ── Global Filters ──
    st.markdown("<p style='color:#94a3b8;font-size:0.85rem;font-weight:600;'>Global Filters</p>", unsafe_allow_html=True)
    g_city  = st.multiselect("City",          sorted(df["city"].dropna().unique()),                placeholder="All cities")
    g_mode  = st.multiselect("Workplace Mode", sorted(df["workplace_mode"].dropna().unique()),      placeholder="All modes")
    g_level = st.multiselect("Career Level",  sorted(df["career_level_short"].dropna().unique()),  placeholder="All levels")

    gdf = df.copy()
    if g_city:  gdf = gdf[gdf["city"].isin(g_city)]
    if g_mode:  gdf = gdf[gdf["workplace_mode"].isin(g_mode)]
    if g_level: gdf = gdf[gdf["career_level_short"].isin(g_level)]

    active = sum([bool(g_city), bool(g_mode), bool(g_level)])
    if active:
        st.markdown(f"<p style='color:#7c8cf8;font-size:0.8rem;'>⚡ {active} filter(s) active — {len(gdf)} jobs</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<p style='color:#64748b;font-size:0.75rem;'>{len(df)} total listings<br>WUZZUF Egypt Dataset</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE 1 — MARKET OVERVIEW
# ═══════════════════════════════════════════════════════
if page == "Market Overview":
    st.markdown("<div class='page-title'>Market Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>A bird's-eye view of Egypt's tech job market on WUZZUF</div>", unsafe_allow_html=True)

    all_s_flat = [s for sl in gdf["skills_list"] for s in sl]

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(metric_card(len(gdf), "Total Listings"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card(gdf["company_name"].nunique(), "Companies"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card(gdf["city"].nunique(), "Cities"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card(f"{round((gdf['is_remote'].mean()+gdf['is_hybrid'].mean())*100)}%", "Remote/Hybrid"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card(len(set(all_s_flat)), "Unique Skills"), unsafe_allow_html=True)

    # ── Auto Insights ──
    st.markdown("<div class='section-header'>Auto Insights</div>", unsafe_allow_html=True)

    skill_counter_all = Counter(all_s_flat)
    top_skill = skill_counter_all.most_common(1)[0] if skill_counter_all else ("N/A", 0)
    top_skill_pct = round(top_skill[1] / len(gdf) * 100) if len(gdf) else 0
    it_pct        = round(len(gdf[gdf["primary_category"] == "IT/Software"]) / len(gdf) * 100) if len(gdf) else 0
    onsite_pct    = round(gdf["is_onsite"].mean() * 100) if len(gdf) else 0
    top_city      = gdf["city"].value_counts().idxmax() if len(gdf) else "N/A"
    top_city_pct  = round(gdf["city"].value_counts().max() / len(gdf) * 100) if len(gdf) else 0
    entry_pct     = round(len(gdf[gdf["career_level_short"].str.contains("Entry", na=False)]) / len(gdf) * 100) if len(gdf) else 0
    sal_pct       = round(gdf["salary_disclosed"].mean() * 100) if len(gdf) else 0

    insights = [
        ("", f"<span class='insight-highlight'>{top_skill[0].title()}</span> is the most demanded skill, appearing in <span class='insight-highlight'>{top_skill_pct}%</span> of all listings."),
        ("", f"<span class='insight-highlight'>{it_pct}%</span> of all jobs are in IT/Software — the market is heavily tech-skewed."),
        ("", f"<span class='insight-highlight'>{top_city}</span> dominates with <span class='insight-highlight'>{top_city_pct}%</span> of listings — geographic concentration is high."),
        ("", f"Only <span class='insight-highlight'>{100 - onsite_pct}%</span> of jobs offer remote or hybrid — most employers still require on-site."),
        ("", f"<span class='insight-highlight'>{entry_pct}%</span> of listings are entry-level — {'decent' if entry_pct > 15 else 'limited'} opportunities for fresh grads."),
        ("", f"Only <span class='insight-highlight'>{sal_pct}%</span> of companies disclose salary — compensation transparency remains low."),
    ]

    ic1, ic2 = st.columns(2)
    for i, (icon, text) in enumerate(insights):
        with (ic1 if i % 2 == 0 else ic2):
            st.markdown(f"""<div class='insight-card'>
                <div class='insight-icon'>{icon}</div>
                <div class='insight-text'>{text}</div>
            </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Job Categories</div>", unsafe_allow_html=True)
        cat_counts = gdf["primary_category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig = px.bar(cat_counts, x="Count", y="Category", orientation="h", text="Count", color="Count",
                     color_continuous_scale=["#3730a3", "#7c8cf8"])
        fig.update_traces(textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_xaxes(gridcolor="#2a2d3e")
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Workplace Mode</div>", unsafe_allow_html=True)
        wm = gdf["workplace_mode"].value_counts().reset_index()
        wm.columns = ["Mode", "Count"]
        fig2 = px.pie(wm, names="Mode", values="Count", hole=0.55,
                      color_discrete_sequence=["#7c8cf8", "#a78bfa", "#60a5fa"])
        fig2.update_layout(**PLOTLY_LAYOUT)
        fig2.update_traces(textinfo="label+percent", textfont_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Jobs by City</div>", unsafe_allow_html=True)
        city_counts = gdf["city"].value_counts().reset_index()
        city_counts.columns = ["City", "Count"]
        fig3 = px.bar(city_counts, x="City", y="Count", color="Count",
                      color_continuous_scale=["#1e3a5f", "#60a5fa"])
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig3.update_xaxes(gridcolor="rgba(0,0,0,0)")
        fig3.update_yaxes(gridcolor="#2a2d3e")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Career Level Distribution</div>", unsafe_allow_html=True)
        cl = gdf["career_level_short"].value_counts().reset_index()
        cl.columns = ["Level", "Count"]
        fig4 = px.pie(cl, names="Level", values="Count", hole=0.55,
                      color_discrete_sequence=["#34d399", "#60a5fa", "#a78bfa", "#fb923c"])
        fig4.update_layout(**PLOTLY_LAYOUT)
        fig4.update_traces(textinfo="label+percent", textfont_color="white")
        st.plotly_chart(fig4, use_container_width=True)

    # Skills Heatmap
    st.markdown("<div class='section-header'>Skills Heatmap — Top Skills × Job Categories</div>", unsafe_allow_html=True)
    top_skills_overall = [s for s, _ in get_top_skills(gdf, 15)]
    categories = gdf["primary_category"].value_counts().head(6).index.tolist()
    heatmap_data = []
    for cat in categories:
        cat_df = gdf[gdf["primary_category"] == cat]
        cat_skills = Counter([s for sl in cat_df["skills_list"] for s in sl])
        total = len(cat_df)
        for skill in top_skills_overall:
            heatmap_data.append({"Category": cat, "Skill": skill,
                                  "Frequency (%)": round(cat_skills.get(skill, 0) / total * 100, 1)})
    hm_df = pd.DataFrame(heatmap_data)
    hm_pivot = hm_df.pivot(index="Category", columns="Skill", values="Frequency (%)")
    fig_hm = px.imshow(hm_pivot, color_continuous_scale=["#1e2130", "#3730a3", "#7c8cf8", "#a78bfa"],
                       aspect="auto", text_auto=True)
    fig_hm.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=True, xaxis_title="", yaxis_title="")
    fig_hm.update_xaxes(tickangle=-35)
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("<div class='section-header'>Top 20 In-Demand Skills</div>", unsafe_allow_html=True)
    s_df = pd.DataFrame(get_top_skills(gdf, 20), columns=["Skill", "Count"])
    fig5 = px.bar(s_df, x="Skill", y="Count", color="Count",
                  color_continuous_scale=["#3730a3", "#7c8cf8", "#a78bfa"])
    fig5.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig5.update_xaxes(tickangle=-35, gridcolor="rgba(0,0,0,0)")
    fig5.update_yaxes(gridcolor="#2a2d3e")
    st.plotly_chart(fig5, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE 2: SKILL GAP ANALYZER
# ═══════════════════════════════════════════════════════
elif page == "Skill Gap Analyzer":
    st.markdown("<div class='page-title'>Skill Gap Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Enter your skills and target role — see exactly what you're missing</div>", unsafe_allow_html=True)

    col_filters, col_results = st.columns([1, 2])

    with col_filters:
        st.markdown("<div class='section-header'>Your Target</div>", unsafe_allow_html=True)

        target_category = st.selectbox(
            "Job Category",
            ["All"] + sorted(df["primary_category"].dropna().unique().tolist()),
        )
        target_domain = st.selectbox(
            "Job Domain (optional)",
            ["All"] + sorted(df["job_domain_group"].dropna().unique().tolist()),
        )
        target_level = st.selectbox(
            "Career Level",
            ["All"] + sorted(df["career_level_short"].dropna().unique().tolist()),
        )

        st.markdown("<div class='section-header'>Your Skills</div>", unsafe_allow_html=True)
        user_skills_raw = st.text_area(
            "Enter your skills (comma-separated)",
            placeholder="e.g. python, sql, django, git, communication",
            height=120,
        )

        top_n = st.slider("Show top N required skills", 5, 30, 15)
        analyze_btn = st.button("Analyze My Gap", use_container_width=True, type="primary")

    with col_results:
        if analyze_btn and user_skills_raw.strip():
            # Parse user skills
            user_skills = {s.strip().lower() for s in user_skills_raw.split(",") if s.strip()}

            # Filter jobs
            filtered = df.copy()
            if target_category != "All":
                filtered = filtered[filtered["primary_category"] == target_category]
            if target_domain != "All":
                filtered = filtered[filtered["job_domain_group"] == target_domain]
            if target_level != "All":
                filtered = filtered[filtered["career_level_short"] == target_level]

            if len(filtered) == 0:
                st.warning("No jobs match this filter combination. Try relaxing the filters.")
            else:
                # Compute skill frequencies
                skill_counter = Counter([s for sl in filtered["skills_list"] for s in sl])
                top_skills_list = skill_counter.most_common(top_n)
                top_skills_set = {s for s, _ in top_skills_list}
                total_jobs = len(filtered)

                matched = user_skills & top_skills_set
                missing = top_skills_set - user_skills
                extra = user_skills - top_skills_set  # skills user has but not in top N

                match_pct = round(len(matched) / len(top_skills_set) * 100) if top_skills_set else 0

                # ── Match Score ──
                st.markdown(f"### Analyzing {total_jobs} matching jobs")

                score_color = "#4ade80" if match_pct >= 60 else "#fb923c" if match_pct >= 35 else "#f87171"
                st.markdown(f"""
                <div style='background:#1e2130;border-radius:12px;padding:20px;border:1px solid #2a2d3e;margin-bottom:16px;'>
                    <div style='font-size:0.85rem;color:#64748b;'>Your match score against top {top_n} required skills</div>
                    <div style='font-size:3rem;font-weight:700;color:{score_color};'>{match_pct}%</div>
                    <div class='gap-bar-container'>
                        <div class='gap-bar-fill' style='width:{match_pct}%;background:linear-gradient(90deg,{score_color},{score_color}aa);'></div>
                    </div>
                    <div style='color:#64748b;font-size:0.8rem;margin-top:6px;'>
                        {len(matched)} matched &nbsp;|&nbsp;  {len(missing)}missing &nbsp;|&nbsp; {len(extra)} extra skills you have
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Missing Skills ──
                st.markdown("<div class='section-header'>Skills You're Missing (Priority Order)</div>", unsafe_allow_html=True)
                missing_sorted = sorted(missing, key=lambda s: skill_counter.get(s, 0), reverse=True)
                tags_html = ""
                for s in missing_sorted:
                    freq = round(skill_counter[s] / total_jobs * 100)
                    tags_html += f"<span class='skill-tag-missing'>{s} &nbsp;<b>{freq}%</b></span>"
                st.markdown(tags_html, unsafe_allow_html=True)

                st.markdown("")

                # ── Matched Skills ──
                st.markdown("<div class='section-header'>Skills You Already Have (In Demand)</div>", unsafe_allow_html=True)
                matched_sorted = sorted(matched, key=lambda s: skill_counter.get(s, 0), reverse=True)
                tags_html2 = ""
                for s in matched_sorted:
                    freq = round(skill_counter[s] / total_jobs * 100)
                    tags_html2 += f"<span class='skill-tag-match'>{s} &nbsp;<b>{freq}%</b></span>"
                st.markdown(tags_html2, unsafe_allow_html=True)

                if extra:
                    st.markdown("")
                    st.markdown("<div class='section-header'>Your Other Skills (Not in Top Required)</div>", unsafe_allow_html=True)
                    tags_html3 = "".join(f"<span class='skill-tag-neutral'>{s}</span>" for s in sorted(extra))
                    st.markdown(tags_html3, unsafe_allow_html=True)

                # ── Top Skills Bar Chart ──
                st.markdown("")
                st.markdown("<div class='section-header'>Full Skill Demand Breakdown</div>", unsafe_allow_html=True)
                skills_plot = pd.DataFrame(top_skills_list, columns=["Skill", "Jobs"])
                skills_plot["Freq%"] = (skills_plot["Jobs"] / total_jobs * 100).round(1)
                skills_plot["Status"] = skills_plot["Skill"].apply(
                    lambda s: "You have it" if s in user_skills else "You're missing it"
                )
                fig = px.bar(skills_plot, x="Freq%", y="Skill", orientation="h",
                             color="Status", text="Freq%",
                             color_discrete_map={"You have it": "#4ade80", "You're missing it": "#f87171"})
                fig.update_traces(texttemplate="%{text}%", textposition="outside")
                fig.update_layout(**PLOTLY_LAYOUT, yaxis=dict(categoryorder="total ascending"),
                                  legend=dict(orientation="h", y=1.05))
                fig.update_xaxes(gridcolor="#2a2d3e", title="% of Job Listings")
                fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

        elif analyze_btn:
            st.warning("Please enter at least one skill to analyze.")
        else:
            st.markdown("""
            <div style='background:#1e2130;border-radius:12px;padding:30px;border:1px dashed #3a3f5c;text-align:center;margin-top:20px;'>
                <div style='font-size:2.5rem;'>🎯</div>
                <div style='color:#64748b;margin-top:10px;'>Fill in your target filters and skills on the left,<br>then hit <b style='color:#7c8cf8;'>Analyze My Gap</b></div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE 3 — SKILL SEARCH
# ═══════════════════════════════════════════════════════
elif page == "Skill Search":
    st.markdown("<div class='page-title'>Skill Search</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Pick any skill — see who needs it, at what level, where, and what pairs with it</div>", unsafe_allow_html=True)

    all_skills_flat = sorted(set([s for sl in gdf["skills_list"] for s in sl]))

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        selected_skill = st.selectbox("Choose a skill", all_skills_flat)
    with col_s2:
        compare_skill = st.selectbox("Compare with (optional)", ["None"] + all_skills_flat)

    skill_jobs   = gdf[gdf["skills_list"].apply(lambda sl: selected_skill in sl)]
    compare_jobs = gdf[gdf["skills_list"].apply(lambda sl: compare_skill in sl)] if compare_skill != "None" else None

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card(len(skill_jobs), f"Jobs needing this skill"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card(f"{round(len(skill_jobs)/len(gdf)*100)}%", "Of all listings"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card(skill_jobs["company_name"].nunique(), "Companies"), unsafe_allow_html=True)
    with c4:
        sal_j = skill_jobs[skill_jobs["salary_disclosed"] == True]
        med_sal = f"EGP {int(sal_j['sal_max_egp'].median()):,}" if len(sal_j) > 0 else "N/A"
        st.markdown(metric_card(med_sal, "Median Max Salary"), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>By Career Level</div>", unsafe_allow_html=True)
        level_counts = skill_jobs["career_level_short"].value_counts().reset_index()
        level_counts.columns = ["Level", "Count"]
        if compare_jobs is not None:
            cmp_lv = compare_jobs["career_level_short"].value_counts().reset_index()
            cmp_lv.columns = ["Level", "Count2"]
            merged = level_counts.merge(cmp_lv, on="Level", how="outer").fillna(0)
            fig = go.Figure()
            fig.add_trace(go.Bar(name=selected_skill, x=merged["Level"], y=merged["Count"], marker_color="#7c8cf8"))
            fig.add_trace(go.Bar(name=compare_skill,  x=merged["Level"], y=merged["Count2"], marker_color="#f472b6"))
            fig.update_layout(**PLOTLY_LAYOUT, barmode="group", legend=dict(orientation="h", y=1.1))
        else:
            fig = px.bar(level_counts, x="Level", y="Count", color="Count",
                         color_continuous_scale=["#3730a3", "#7c8cf8"])
            fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig.update_xaxes(gridcolor="rgba(0,0,0,0)")
        fig.update_yaxes(gridcolor="#2a2d3e")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>By Workplace Mode</div>", unsafe_allow_html=True)
        mode_counts = skill_jobs["workplace_mode"].value_counts().reset_index()
        mode_counts.columns = ["Mode", "Count"]
        if compare_jobs is not None:
            cmp_md = compare_jobs["workplace_mode"].value_counts().reset_index()
            cmp_md.columns = ["Mode", "Count2"]
            merged_m = mode_counts.merge(cmp_md, on="Mode", how="outer").fillna(0)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name=selected_skill, x=merged_m["Mode"], y=merged_m["Count"], marker_color="#7c8cf8"))
            fig2.add_trace(go.Bar(name=compare_skill,  x=merged_m["Mode"], y=merged_m["Count2"], marker_color="#f472b6"))
            fig2.update_layout(**PLOTLY_LAYOUT, barmode="group", legend=dict(orientation="h", y=1.1))
        else:
            fig2 = px.pie(mode_counts, names="Mode", values="Count", hole=0.5,
                          color_discrete_sequence=["#7c8cf8", "#a78bfa", "#60a5fa"])
            fig2.update_layout(**PLOTLY_LAYOUT)
            fig2.update_traces(textinfo="label+percent", textfont_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Top Companies Needing This Skill</div>", unsafe_allow_html=True)
        comp_counts = (skill_jobs[skill_jobs["company_name"] != "Confidential"]["company_name"]
                       .value_counts().head(10).reset_index())
        comp_counts.columns = ["Company", "Count"]
        fig3 = px.bar(comp_counts, x="Count", y="Company", orientation="h", text="Count", color="Count",
                      color_continuous_scale=["#1e3a5f", "#60a5fa"])
        fig3.update_traces(textposition="outside")
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
        fig3.update_xaxes(gridcolor="#2a2d3e")
        fig3.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Skills That Co-occur With This Skill</div>", unsafe_allow_html=True)
        co_skills = Counter([s for sl in skill_jobs["skills_list"] for s in sl if s != selected_skill]).most_common(12)
        if co_skills:
            co_df = pd.DataFrame(co_skills, columns=["Skill", "Count"])
            co_df["Freq%"] = (co_df["Count"] / len(skill_jobs) * 100).round(1)
            fig4 = px.bar(co_df, x="Freq%", y="Skill", orientation="h", text="Freq%", color="Freq%",
                          color_continuous_scale=["#1a3a2a", "#34d399"])
            fig4.update_traces(texttemplate="%{text}%", textposition="outside")
            fig4.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                               yaxis=dict(categoryorder="total ascending"),
                               xaxis_title="% of jobs with this skill that also need:")
            fig4.update_xaxes(gridcolor="#2a2d3e")
            fig4.update_yaxes(gridcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE 4 — SALARY INTELLIGENCE
# ═══════════════════════════════════════════════════════
elif page == "Salary Intelligence":
    st.markdown("<div class='page-title'>Salary Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Based on disclosed salaries only — 36 of 411 jobs (8.7%)</div>", unsafe_allow_html=True)

    sal_df = gdf[gdf["salary_disclosed"] == True].copy()

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(metric_card(f"EGP {int(sal_df['sal_min_egp'].median()):,}", "Median Min Salary"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card(f"EGP {int(sal_df['sal_max_egp'].median()):,}", "Median Max Salary"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card(len(sal_df), "Jobs with Salary Data"), unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-header'>Salary Range by Career Level</div>", unsafe_allow_html=True)
        sal_level = sal_df.groupby("career_level_short").agg(
            min_sal=("sal_min_egp", "median"), max_sal=("sal_max_egp", "median")
        ).reset_index().sort_values("min_sal")
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Median Min", x=sal_level["career_level_short"], y=sal_level["min_sal"], marker_color="#7c8cf8"))
        fig.add_trace(go.Bar(name="Median Max", x=sal_level["career_level_short"], y=sal_level["max_sal"], marker_color="#a78bfa"))
        fig.update_layout(**PLOTLY_LAYOUT, barmode="group", yaxis_title="EGP/Month",
                          legend=dict(orientation="h", y=1.05))
        fig.update_xaxes(gridcolor="rgba(0,0,0,0)")
        fig.update_yaxes(gridcolor="#2a2d3e")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-header'>Salary Distribution</div>", unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Box(y=sal_df["sal_min_egp"], name="Min Salary", marker_color="#60a5fa", boxmean=True))
        fig2.add_trace(go.Box(y=sal_df["sal_max_egp"], name="Max Salary", marker_color="#a78bfa", boxmean=True))
        fig2.update_layout(**PLOTLY_LAYOUT, yaxis_title="EGP/Month")
        fig2.update_yaxes(gridcolor="#2a2d3e")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>All Salary Listings</div>", unsafe_allow_html=True)
    st.dataframe(
        sal_df[["job_title", "company_name", "city", "career_level_short", "workplace_mode", "sal_min_egp", "sal_max_egp"]]
        .rename(columns={"career_level_short": "Level", "workplace_mode": "Mode",
                          "sal_min_egp": "Min (EGP)", "sal_max_egp": "Max (EGP)"})
        .sort_values("Max (EGP)", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )


# ═══════════════════════════════════════════════════════
# PAGE 5 — COMPANY EXPLORER
# ═══════════════════════════════════════════════════════
elif page == "Company Explorer":
    st.markdown("<div class='page-title'>Company Explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Who's hiring, what they need, and how flexible they are</div>", unsafe_allow_html=True)

    show_conf = st.checkbox("Include 'Confidential' postings", value=False)
    comp_df = gdf if show_conf else gdf[gdf["company_name"] != "Confidential"]

    company_stats = comp_df.groupby("company_name").agg(
        postings=("job_title", "count"),
        remote_pct=("is_remote", "mean"),
        hybrid_pct=("is_hybrid", "mean"),
    ).reset_index().sort_values("postings", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Top Hiring Companies</div>", unsafe_allow_html=True)
        fig = px.bar(company_stats.head(15), x="postings", y="company_name",
                     orientation="h", text="postings", color="postings",
                     color_continuous_scale=["#1e3a5f", "#7c8cf8"])
        fig.update_traces(textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
        fig.update_xaxes(gridcolor="#2a2d3e")
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Remote/Hybrid Friendliness</div>", unsafe_allow_html=True)
        flex_df = company_stats[company_stats["postings"] >= 3].copy()
        flex_df["flexible_pct"] = ((flex_df["remote_pct"] + flex_df["hybrid_pct"]) * 100).round(1)
        flex_df = flex_df.sort_values("flexible_pct", ascending=False).head(12)
        fig2 = px.bar(flex_df, x="flexible_pct", y="company_name", orientation="h",
                      text="flexible_pct", color="flexible_pct",
                      color_continuous_scale=["#1a3a2a", "#34d399"])
        fig2.update_traces(texttemplate="%{text}%", textposition="outside")
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                           xaxis_title="% Remote or Hybrid", yaxis=dict(categoryorder="total ascending"))
        fig2.update_xaxes(gridcolor="#2a2d3e")
        fig2.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Company Deep Dive</div>", unsafe_allow_html=True)
    selected_company = st.selectbox("Select a company", company_stats["company_name"].tolist())
    comp_jobs = comp_df[comp_df["company_name"] == selected_company]

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(metric_card(len(comp_jobs), "Open Listings"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card(comp_jobs["city"].nunique(), "Cities"), unsafe_allow_html=True)
    with c3:
        flex = comp_jobs["is_remote"].sum() + comp_jobs["is_hybrid"].sum()
        st.markdown(metric_card(f"{flex}/{len(comp_jobs)}", "Remote/Hybrid"), unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Open Roles**")
        st.dataframe(comp_jobs[["job_title", "city", "career_level_short", "workplace_mode"]]
                     .rename(columns={"career_level_short": "Level", "workplace_mode": "Mode"})
                     .reset_index(drop=True), use_container_width=True)
    with col_b:
        st.markdown("**Top Skills Needed**")
        comp_skills = Counter([s for sl in comp_jobs["skills_list"] for s in sl]).most_common(12)
        if comp_skills:
            st.markdown("".join(f"<span class='skill-tag-neutral'>{s}</span>" for s, _ in comp_skills), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE 6 — CAREER PATH PLANNER
# ═══════════════════════════════════════════════════════
elif page == "Career Path Planner":
    st.markdown("<div class='page-title'>Career Path Planner</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>What does it take to reach your target level?</div>", unsafe_allow_html=True)

    col_f, col_r = st.columns([1, 2])
    with col_f:
        st.markdown("<div class='section-header'>Choose Your Target</div>", unsafe_allow_html=True)
        target_cat2 = st.selectbox("Job Category", ["All"] + sorted(gdf["primary_category"].dropna().unique().tolist()), key="cpp_cat")
        target_dom2 = st.selectbox("Job Domain",   ["All"] + sorted(gdf["job_domain_group"].dropna().unique().tolist()),  key="cpp_dom")

    filtered2 = gdf.copy()
    if target_cat2 != "All": filtered2 = filtered2[filtered2["primary_category"] == target_cat2]
    if target_dom2 != "All": filtered2 = filtered2[filtered2["job_domain_group"] == target_dom2]

    with col_r:
        if len(filtered2) == 0:
            st.warning("No data for this combination.")
        else:
            exp_df = filtered2.groupby("career_level_short").agg(
                min_exp=("years_exp_min", "median"), max_exp=("years_exp_max", "median"), count=("job_title", "count")
            ).reset_index().dropna()
            order_map = {"Entry Level": 0, "Experienced (Non-Manager)": 1, "Manager": 2, "Senior Management": 3}
            exp_df["sort"] = exp_df["career_level_short"].map(order_map)
            exp_df = exp_df.sort_values("sort")

            st.markdown(f"<p style='color:#64748b;'>Based on {len(filtered2)} listings</p>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>Experience Required by Level</div>", unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Min Years", x=exp_df["career_level_short"], y=exp_df["min_exp"], marker_color="#60a5fa"))
            fig.add_trace(go.Bar(name="Max Years", x=exp_df["career_level_short"], y=exp_df["max_exp"], marker_color="#a78bfa"))
            fig.update_layout(**PLOTLY_LAYOUT, barmode="group", yaxis_title="Years",
                              legend=dict(orientation="h", y=1.05))
            fig.update_xaxes(gridcolor="rgba(0,0,0,0)")
            fig.update_yaxes(gridcolor="#2a2d3e")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Top Skills Required at Each Level</div>", unsafe_allow_html=True)
    level_order   = ["Entry Level", "Experienced (Non-Manager)", "Manager", "Senior Management"]
    levels_present = [l for l in level_order if l in filtered2["career_level_short"].values]
    cols = st.columns(min(len(levels_present), 4))

    for i, level in enumerate(levels_present):
        level_jobs   = filtered2[filtered2["career_level_short"] == level]
        level_skills = Counter([s for sl in level_jobs["skills_list"] for s in sl]).most_common(8)
        with cols[i % len(cols)]:
            st.markdown(f"**{level}** <span style='color:#64748b;font-size:0.75rem;'>({len(level_jobs)} jobs)</span>", unsafe_allow_html=True)
            for skill, count in level_skills:
                pct = round(count / len(level_jobs) * 100)
                st.markdown(f"""
                <div style='margin-bottom:6px;'>
                    <div style='display:flex;justify-content:space-between;font-size:0.8rem;color:#c5c9e0;'>
                        <span>{skill}</span><span>{pct}%</span>
                    </div>
                    <div class='gap-bar-container' style='height:6px;'>
                        <div class='gap-bar-fill' style='width:{pct}%;'></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Education Requirements by Level</div>", unsafe_allow_html=True)
    edu_data = filtered2.groupby(["career_level_short", "education_level"]).size().reset_index(name="count")
    fig_edu = px.bar(edu_data, x="career_level_short", y="count", color="education_level",
                     barmode="stack", color_discrete_sequence=px.colors.sequential.Plasma_r)
    fig_edu.update_layout(**PLOTLY_LAYOUT, xaxis_title="", yaxis_title="# of Jobs",
                           legend=dict(orientation="h", y=1.05, font=dict(size=10)))
    fig_edu.update_xaxes(gridcolor="rgba(0,0,0,0)")
    fig_edu.update_yaxes(gridcolor="#2a2d3e")
    st.plotly_chart(fig_edu, use_container_width=True)