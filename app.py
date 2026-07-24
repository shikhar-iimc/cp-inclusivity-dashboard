"""
Class Participation as a Site of Structural Exclusion
IDT: Inclusivity - Group 16, Section D, IIM Calcutta

Interactive survey dashboard. All data is embedded as ANONYMOUS AGGREGATE
COUNTS (N = 50); no response-level data, names, or emails are stored here.
To update numbers, edit the COUNTS / DEMO dictionaries and redeploy.
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Class Participation - Group 16, Section D",
                   layout="wide", initial_sidebar_state="collapsed")

# ---- palette (dark, readable; colour used sparingly for emphasis) ----
INK = "#1A1A1A"      # body text (dark, not grey)
SOFT = "#3D3D3D"     # secondary text (still clearly readable)
FAINT = "#6E6E6E"    # captions only, kept dark enough to read
HAIR = "#E2E2E2"     # hairlines
BG = "#FFFFFF"
RED = "#A62A21"      # emphasis: a number that is a problem
GREEN = "#2E6B4F"    # emphasis: the healthy contrast
BAR = "#333333"      # default bar
BAR_SOFT = "#BFBFBF" # de-emphasised bar

# ======================================================================
# EMBEDDED AGGREGATE DATA  (N = 50, anonymous counts only)
# ======================================================================
N = 50
COUNTS = {
    "full":     {1: 6,  2: 6, 3: 17, 4: 11, 5: 10},
    "small":    {1: 1,  2: 3, 3: 7,  4: 18, 5: 21},
    "rehearse": {1: 3,  2: 3, 3: 8,  4: 20, 5: 16},
    "written":  {1: 1,  2: 2, 3: 15, 4: 16, 5: 16},
    "fair":     {1: 15, 2: 8, 3: 14, 4: 10, 5: 3},
}
MISSED = {"Never": 3, "Rarely": 3, "Sometimes": 19, "Often": 18, "Very often": 7}
DEMO_MEDIUM = {"Primarily English": 42, "Mixed": 5, "Primarily a regional language": 3}
DEMO_EXP = {"Fresher (0-1 yr)": 29, "1-3 years": 17, "3-6 years": 4}
TONE = [("Critical / wants reform", 7, RED), ("Neutral", 1, BAR_SOFT), ("Satisfied", 1, GREEN)]
N_OPEN = 9
GFORM_RESPONSES_LINK = "[INSERT_GOOGLE_FORM_RESPONSES_LINK]"

# ---- css --------------------------------------------------------------
st.markdown(f"""
<style>
  /* force light rendering even if the viewer's browser/OS is in dark mode */
  .stApp {{ background:{BG} !important; }}
  [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, section.main {{ background:{BG} !important; }}
  html, body, [class*="css"] {{ color:{INK} !important; background:{BG} !important; }}
  [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {{ color:{INK}; }}
  .block-container {{ max-width:1060px; padding-top:2.2rem; padding-bottom:3.5rem; background:{BG} !important; }}
  h1,h2,h3,h4 {{ font-family:Georgia,'Times New Roman',serif !important; color:{INK} !important; font-weight:normal; }}
  p,li,div,span,label,td,th {{ font-family:Georgia,'Times New Roman',serif; color:{INK}; }}
  .title {{ font-size:2.0rem; line-height:1.15; margin:0 0 6px 0; }}
  .dek {{ color:{SOFT}; font-size:1.02rem; font-style:italic; margin-bottom:4px; }}
  .meta {{ color:{FAINT}; font-size:.8rem; font-family:Helvetica,Arial,sans-serif; letter-spacing:.4px; }}
  .rule {{ border:0; border-top:1px solid {INK}; margin:12px 0 14px 0; }}
  .lead {{ font-size:1.05rem; color:{INK}; line-height:1.55; }}
  .lead .r {{ color:{RED}; font-weight:bold; }}
  .lead .g {{ color:{GREEN}; font-weight:bold; }}
  .h {{ font-size:1.32rem; margin:6px 0 2px 0; }}
  .cap {{ color:{SOFT}; font-size:.9rem; line-height:1.5; font-family:Helvetica,Arial,sans-serif; }}
  .chartlab {{ font-size:.92rem; color:{INK}; font-family:Helvetica,Arial,sans-serif; font-weight:600; margin-bottom:-4px; }}
  .foot {{ color:{SOFT}; font-size:.86rem; font-family:Helvetica,Arial,sans-serif; line-height:1.5; }}
  .foot a {{ color:{INK}; }}
  hr.sec {{ border:0; border-top:1px solid {HAIR}; margin:30px 0 8px 0; }}
  #MainMenu, footer, header {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)

# ---- helpers ----------------------------------------------------------
def arr(c):
    o = []
    for k, v in COUNTS[c].items():
        o += [k] * v
    return np.array(o, float)
def dist(c): return [COUNTS[c].get(i, 0) for i in range(1, 6)]
def mean(c): return arr(c).mean()
def pct_hi(c): return (arr(c) >= 4).mean() * 100
def pct_lo(c): return (arr(c) <= 2).mean() * 100
def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x); cc = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cc) / cc[-1]) / n
def lorenz(x):
    x = np.sort(np.asarray(x, float)); c = np.insert(np.cumsum(x), 0, 0); c = c / c[-1]
    return np.linspace(0, 1, len(c)), c

gap = mean("small") - mean("full")
fair_hi, fair_lo = pct_hi("fair"), pct_lo("fair")
morder = ["Never", "Rarely", "Sometimes", "Often", "Very often"]
mcount = [MISSED[k] for k in morder]
missed_oftenish = (MISSED["Often"] + MISSED["Very often"]) / N * 100
gini_full, gini_small = gini(arr("full")), gini(arr("small"))

def layout(h=250):
    return dict(template="simple_white", height=h, paper_bgcolor=BG, plot_bgcolor=BG,
                font=dict(family="Georgia, serif", color=INK, size=13),
                margin=dict(l=8, r=8, t=10, b=10), showlegend=False,
                hoverlabel=dict(bgcolor=INK, font=dict(color="#FFFFFF", size=12,
                                family="Helvetica, Arial, sans-serif"), bordercolor=INK))

def likert(col, labels, emph_low=False):
    """Mostly neutral bars; a single accent colour marks the meaningful tail."""
    v = dist(col)
    if emph_low:   # low ratings are the concern (e.g. fairness)
        colors = [RED, RED, BAR_SOFT, BAR, BAR]
    else:          # high ratings carry the signal (rehearse, written)
        colors = [BAR_SOFT, BAR_SOFT, BAR, BAR, BAR]
    fig = go.Figure(go.Bar(x=[1, 2, 3, 4, 5], y=v, marker_color=colors, width=0.7,
                           text=v, textposition="outside", textfont=dict(size=13, color=INK),
                           cliponaxis=False, hovertemplate="Rating %{x}: %{y}<extra></extra>"))
    fig.update_layout(**layout(240))
    fig.update_xaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5], ticktext=labels,
                     tickfont=dict(size=11, color=SOFT))
    fig.update_yaxes(visible=False, range=[0, max(v) * 1.25])
    return fig

# ======================= HEADER =======================
st.markdown('<div class="meta">IDT · INCLUSIVITY · IIM CALCUTTA · GROUP 16, SECTION D</div>', unsafe_allow_html=True)
st.markdown('<div class="title">Class Participation as a Site of Structural Exclusion</div>', unsafe_allow_html=True)
st.markdown('<div class="dek">Who the graded classroom rewards, and who it quietly costs.</div>', unsafe_allow_html=True)
st.markdown(f'<div class="meta">Anonymous batch survey · N = {N} · figures are self-reported</div>', unsafe_allow_html=True)
st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ---- lead paragraph replaces the KPI cards ----
st.markdown(
    f'<div class="lead">Class participation looks like the fairest thing we grade: open to anyone willing to speak. '
    f'Yet only <span class="r">{fair_hi:.0f}%</span> of the batch considers it fair, and '
    f'<span class="r">{fair_lo:.0f}%</span> actively disagree. The same students who go quiet in the full section '
    f'become far more willing to speak in a small group, a jump of <span class="r">{gap:.2f}</span> points on a '
    f'five-point scale. Most (<span class="r">{pct_hi("rehearse"):.0f}%</span>) rehearse before they speak, and '
    f'half lose a ready point to a faster voice. What the grade measures, it seems, is comfort with a crowded room, '
    f'not command of the material.</div>',
    unsafe_allow_html=True)

# ======================= 1 · COMFORT GAP =======================
st.markdown('<hr class="sec">', unsafe_allow_html=True)
st.markdown('<div class="h">The barrier is the room, not the student</div>', unsafe_allow_html=True)
st.markdown('<div class="cap">Comfort speaking, rated 1 to 5, in two settings. The same people, a different level of '
            'exposure. If comfort climbs when the room shrinks, participation is tracking the setting, not understanding.</div>',
            unsafe_allow_html=True)
st.write("")
a, b, c = st.columns(3)
with a:
    st.markdown(f'<div class="chartlab">Full section &nbsp;·&nbsp; mean {mean("full"):.2f}</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("full", ["1", "2", "3", "4", "5"]), use_container_width=True, config={"displayModeBar": False})
with b:
    st.markdown(f'<div class="chartlab">Small group / one-to-one &nbsp;·&nbsp; mean {mean("small"):.2f}</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("small", ["1", "2", "3", "4", "5"]), use_container_width=True, config={"displayModeBar": False})
with c:
    st.markdown(f'<div class="chartlab">"CP grading is fair" &nbsp;·&nbsp; mean {mean("fair"):.2f}</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("fair", ["1", "2", "3", "4", "5"], emph_low=True), use_container_width=True, config={"displayModeBar": False})
st.markdown(f'<div class="cap">Comfort rises {gap:.2f} points from the full section (mean {mean("full"):.2f}) to a small '
            f'group ({mean("small"):.2f}). On fairness, the weight sits on the left: {fair_lo:.0f}% disagree that CP is '
            f'fair against {fair_hi:.0f}% who agree. Scales run 1 (very uncomfortable / strongly disagree) to 5.</div>',
            unsafe_allow_html=True)

# ======================= 2 · HIDDEN TAX =======================
st.markdown('<hr class="sec">', unsafe_allow_html=True)
st.markdown('<div class="h">A hidden tax, and a misread of ability</div>', unsafe_allow_html=True)
st.markdown('<div class="cap">Two questions on what speaking actually costs, and whether the grade captures what a '
            'student knows. Agreement (ratings 4 to 5) shaded darker.</div>', unsafe_allow_html=True)
st.write("")
a, b = st.columns(2)
with a:
    st.markdown(f'<div class="chartlab">"I rehearse in my head before I speak" &nbsp;·&nbsp; {pct_hi("rehearse"):.0f}% agree</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("rehearse", ["1", "2", "3", "4", "5"]), use_container_width=True, config={"displayModeBar": False})
with b:
    st.markdown(f'<div class="chartlab">"My written work reflects me better than my speaking" &nbsp;·&nbsp; {pct_hi("written"):.0f}% agree</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("written", ["1", "2", "3", "4", "5"]), use_container_width=True, config={"displayModeBar": False})
st.markdown('<div class="cap">Most students prepare a contribution before speaking, so fluency in the room is partly '
            'rehearsal capacity. And a clear majority feel their written work represents them better than their speaking, '
            'which is what a grade built on speaking fails to capture.</div>', unsafe_allow_html=True)

# ======================= 3 · AIRTIME =======================
st.markdown('<hr class="sec">', unsafe_allow_html=True)
st.markdown('<div class="h">Airtime is scarce and unevenly shared</div>', unsafe_allow_html=True)
st.write("")
a, b = st.columns(2)
with a:
    st.markdown('<div class="chartlab">"Had a point ready but did not get to say it"</div>', unsafe_allow_html=True)
    cols_m = [BAR_SOFT, BAR_SOFT, BAR_SOFT, BAR, RED]
    fig = go.Figure(go.Bar(x=mcount, y=morder, orientation="h", marker_color=cols_m,
                           text=mcount, textposition="outside", textfont=dict(size=13, color=INK), cliponaxis=False,
                           hovertemplate="%{y}: %{x}<extra></extra>"))
    fig.update_layout(**layout(240))
    fig.update_xaxes(visible=False, range=[0, max(mcount) * 1.2])
    fig.update_yaxes(categoryorder="array", categoryarray=morder[::-1], tickfont=dict(size=11, color=SOFT))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f'<div class="cap"><b style="color:{RED}">{missed_oftenish:.0f}%</b> answered often or very often.</div>', unsafe_allow_html=True)
with b:
    st.markdown(f'<div class="chartlab">Distribution of "voice" (Lorenz) &nbsp;·&nbsp; Gini {gini_full:.2f} full vs {gini_small:.2f} small</div>', unsafe_allow_html=True)
    pf, cf = lorenz(arr("full")); ps, cs = lorenz(arr("small"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=FAINT, dash="dash", width=1), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ps, y=cs, mode="lines", line=dict(color=GREEN, width=2.2), hovertemplate="Small group<extra></extra>"))
    fig.add_trace(go.Scatter(x=pf, y=cf, mode="lines", line=dict(color=RED, width=2.4), hovertemplate="Full section<extra></extra>"))
    fig.update_layout(**layout(240))
    fig.update_xaxes(range=[0, 1], title=dict(text="share of students", font=dict(size=11, color=SOFT)), tickfont=dict(size=10, color=SOFT))
    fig.update_yaxes(range=[0, 1], title=dict(text="share of comfort", font=dict(size=11, color=SOFT)), tickfont=dict(size=10, color=SOFT))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="cap">The further a curve bows below the dashed line of equality, the more unequal the '
                'distribution. Voice is more concentrated in the graded full section (red) than in the small group (green).</div>',
                unsafe_allow_html=True)

# ======================= 4 · WHO + WHAT =======================
st.markdown('<hr class="sec">', unsafe_allow_html=True)
a, b = st.columns([1.05, 1])
with a:
    st.markdown('<div class="h">Who answered</div>', unsafe_allow_html=True)
    st.markdown('<div class="cap">Sample composition. The comfort gap holds across these groups, which is why we read '
                'it as structural rather than a feature of one background.</div>', unsafe_allow_html=True)
    st.write("")
    def compbar(d):
        keys = list(d.keys()); vals = list(d.values())
        fig = go.Figure(go.Bar(x=vals, y=keys, orientation="h", marker_color=BAR,
                               text=vals, textposition="outside", textfont=dict(size=12, color=INK), cliponaxis=False,
                               hovertemplate="%{y}: %{x}<extra></extra>"))
        fig.update_layout(**layout(148))
        fig.update_xaxes(visible=False, range=[0, max(vals) * 1.25])
        fig.update_yaxes(tickfont=dict(size=10.5, color=SOFT), autorange="reversed")
        return fig
    st.markdown('<div class="chartlab">Medium of schooling</div>', unsafe_allow_html=True)
    st.plotly_chart(compbar(DEMO_MEDIUM), use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="chartlab">Work experience</div>', unsafe_allow_html=True)
    st.plotly_chart(compbar(DEMO_EXP), use_container_width=True, config={"displayModeBar": False})
with b:
    st.markdown('<div class="h">What respondents said</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cap">Themes from the {N_OPEN} optional written responses, grouped and paraphrased; '
                f'individual responses are not reproduced. The tone split is illustrative, not statistical, at this small n.</div>',
                unsafe_allow_html=True)
    st.write("")
    fig = go.Figure()
    for lab, val, colr in TONE:
        fig.add_trace(go.Bar(x=[val], y=["t"], orientation="h", marker_color=colr,
                             text=[f"{lab} ({val})"], textposition="inside", insidetextanchor="middle",
                             textfont=dict(color="#fff", size=11), hovertemplate=f"{lab}: {val}<extra></extra>"))
    fig.update_layout(**layout(78), barmode="stack")
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    for head, colr, body in [
        ("Grade quality, not volume", RED, "Marks reward how often you speak rather than the merit of the point; scoring should turn on quality."),
        ("Decouple from, or reduce, the grade", "#8A6D1F", "The incentive drives performative, repetitive talk; lower its weight or reward it some other way."),
        ("It costs class time", "#8A6D1F", "Rushed participation crowds out the material a professor meant to cover, and turns discussion into competition."),
        ("Offer a written channel", GREEN, "Let students submit points in writing, through a live in-class channel with hidden names or a short note, that counts toward CP."),
    ]:
        st.markdown(f'<div style="border-left:3px solid {colr};padding:2px 0 6px 12px;margin-bottom:12px;">'
                    f'<div style="font-family:Georgia,serif;font-size:1.02rem;">{head}</div>'
                    f'<div class="cap" style="margin-top:2px">{body}</div></div>', unsafe_allow_html=True)

# ======================= FOOTER =======================
st.markdown('<hr class="sec">', unsafe_allow_html=True)
st.markdown(
    f'<div class="foot"><b>A note on the data.</b> This is an indicative, self-report survey of {N} respondents, '
    'collected anonymously with no names or emails. It records perceived comfort, effort and fairness, not actual '
    'participation grades, and the sample leans English-medium, engineering and early-career, so the patterns are '
    'suggestive rather than conclusive. All figures are aggregate counts; written responses are paraphrased in '
    'aggregate and never reproduced word for word.</div>', unsafe_allow_html=True)
st.write("")
st.markdown(f'<div class="foot">Full anonymous survey responses: '
            f'<a href="{GFORM_RESPONSES_LINK}" target="_blank">Google Form response sheet</a> '
            f'(link to be added).</div>', unsafe_allow_html=True)
st.markdown('<div class="foot" style="margin-top:10px;color:#6E6E6E">IDT: Inclusivity group project · Group 16, Section D · '
            'IIM Calcutta. Full diagnosis and the proposed intervention are set out in the accompanying report and policy memo.</div>',
            unsafe_allow_html=True)
