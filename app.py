"""
Class Participation as a Site of Structural Exclusion
IDT: Inclusivity - Group 16, Section D, IIM Calcutta

Interactive survey dashboard. All data below is embedded as ANONYMOUS AGGREGATE
COUNTS (N = 50) - no response-level data, names, or emails are stored in this repo.
To update: edit the COUNTS / DEMO dictionaries and redeploy.
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="CP as Structural Exclusion - Group 16",
                   page_icon="▪", layout="wide", initial_sidebar_state="collapsed")

# ---- palette ----------------------------------------------------------
INK = "#141414"; MID = "#5C5C5C"; FAINT = "#8A8A8A"; LINE = "#D8D8D8"; BG = "#FFFFFF"
CRIT = "#C0392B"    # needs action
WARN = "#B7791F"    # concern
GOOD = "#2F7A57"    # healthy
BAR = "#2B2B2B"; BAR_LT = "#C4C4C4"

# ======================================================================
# EMBEDDED AGGREGATE DATA  (N = 50, anonymous counts only)
# ======================================================================
N = 50
COUNTS = {
    "full":     {1: 6,  2: 6, 3: 17, 4: 11, 5: 10},  # comfort, full section
    "small":    {1: 1,  2: 3, 3: 7,  4: 18, 5: 21},  # comfort, small group
    "rehearse": {1: 3,  2: 3, 3: 8,  4: 20, 5: 16},  # rehearse before speaking
    "written":  {1: 1,  2: 2, 3: 15, 4: 16, 5: 16},  # written reflects me better
    "fair":     {1: 15, 2: 8, 3: 14, 4: 10, 5: 3},   # CP grading is fair
}
MISSED = {"Never": 3, "Rarely": 3, "Sometimes": 19, "Often": 18, "Very often": 7}
DEMO_MEDIUM = {"Primarily English": 42, "Mixed": 5, "Primarily a regional language": 3}
DEMO_EXP = {"Fresher (0-1 yr)": 29, "1-3 years": 17, "3-6 years": 4}
# illustrative tone coding of the 9 optional written responses
TONE = [("Critical / wants reform", 7, CRIT), ("Neutral", 1, BAR_LT), ("Satisfied", 1, GOOD)]
N_OPEN = 9

# ---- css: lock light, dense editorial look ---------------------------
st.markdown(f"""
<style>
  .stApp {{ background:{BG}; }}
  html, body, [class*="css"] {{ color:{INK}; }}
  .block-container {{ max-width:1120px; padding-top:1.6rem; padding-bottom:3rem; }}
  h1,h2,h3,h4 {{ font-family:Georgia,'Times New Roman',serif !important; color:{INK} !important; letter-spacing:-.2px; }}
  p,li,div,span,label,td,th {{ font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif; color:{INK}; }}
  .kicker {{ font-family:-apple-system,Segoe UI,sans-serif !important; text-transform:uppercase;
            letter-spacing:2.5px; font-size:.70rem; color:{MID}; }}
  .mast {{ border-bottom:2.5px solid {INK}; padding-bottom:10px; margin-bottom:14px; }}
  .mast h1 {{ font-size:1.9rem; margin:2px 0; }}
  .sub {{ color:{MID}; font-size:.95rem; }}
  .sectitle {{ font-family:Georgia,serif; font-size:1.28rem; margin:6px 0 2px 0; }}
  .claim {{ border-left:3px solid {INK}; padding:2px 0 2px 12px; font-family:Georgia,serif;
            font-size:1.05rem; color:{INK}; margin:2px 0 6px 0; }}
  .note {{ color:{MID}; font-size:.86rem; line-height:1.45; }}
  .tag {{ display:inline-block; font-family:-apple-system,Segoe UI,sans-serif; font-size:.62rem; font-weight:700;
          letter-spacing:1.2px; text-transform:uppercase; padding:2px 7px; border-radius:2px; color:#fff; }}
  .kpi {{ border:1px solid {LINE}; border-top:4px solid {INK}; padding:14px 15px 13px 15px; height:100%; background:#fff; }}
  .kpi .num {{ font-family:Georgia,serif; font-size:2.15rem; line-height:1; }}
  .kpi .lab {{ font-size:.80rem; color:{MID}; margin-top:7px; line-height:1.35; }}
  .band {{ background:{INK}; color:#fff; padding:11px 16px; font-size:.92rem; }}
  .band a {{ color:#fff !important; font-weight:700; }}
  .caveat {{ border:1px solid {INK}; background:#FAFAFA; padding:11px 15px; font-size:.82rem; color:#333; }}
  hr {{ border:0; border-top:1px solid {LINE}; margin:22px 0 4px 0; }}
  #MainMenu, footer, header {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)

# ---- helpers ----------------------------------------------------------
def arr(col):
    out = []
    for k, v in COUNTS[col].items():
        out += [k] * v
    return np.array(out, float)
def dist(col): return [COUNTS[col].get(i, 0) for i in range(1, 6)]
def mean(col): return arr(col).mean()
def pct_hi(col): return (arr(col) >= 4).mean() * 100
def pct_lo(col): return (arr(col) <= 2).mean() * 100
def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x); c = np.cumsum(x)
    return (n + 1 - 2 * np.sum(c) / c[-1]) / n
def lorenz(x):
    x = np.sort(np.asarray(x, float)); c = np.insert(np.cumsum(x), 0, 0); c = c / c[-1]
    return np.linspace(0, 1, len(c)), c

gap = mean("small") - mean("full")
fair_hi, fair_lo = pct_hi("fair"), pct_lo("fair")
morder = ["Never", "Rarely", "Sometimes", "Often", "Very often"]
mcount = [MISSED[k] for k in morder]
missed_oftenish = (MISSED["Often"] + MISSED["Very often"]) / N * 100
gini_full, gini_small = gini(arr("full")), gini(arr("small"))

def base_layout(h=250):
    return dict(template="simple_white", height=h, paper_bgcolor=BG, plot_bgcolor=BG,
                font=dict(family="Helvetica, Arial, sans-serif", color=INK, size=13),
                margin=dict(l=10, r=10, t=12, b=10), showlegend=False,
                hoverlabel=dict(bgcolor="#fff", font_size=12, bordercolor=INK))

def likert(col, labels, good_high=True):
    v = dist(col)
    colors = ([CRIT, CRIT, BAR_LT, GOOD, GOOD] if good_high else [GOOD, GOOD, BAR_LT, WARN, CRIT])
    fig = go.Figure(go.Bar(x=[1, 2, 3, 4, 5], y=v, marker_color=colors, width=0.72,
                           text=v, textposition="outside", textfont=dict(size=13, color=INK),
                           cliponaxis=False,
                           hovertemplate="Rating %{x}: %{y} respondents<extra></extra>"))
    fig.update_layout(**base_layout(250))
    fig.update_xaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5], ticktext=labels, tickfont=dict(size=11))
    fig.update_yaxes(visible=False, range=[0, max(v) * 1.24])
    return fig

def signal(value, lo, hi, direction):
    if direction == "low_bad":
        return (CRIT, "CRITICAL") if value < lo else (WARN, "CONCERN") if value < hi else (GOOD, "HEALTHY")
    return (CRIT, "CRITICAL") if value > hi else (WARN, "CONCERN") if value > lo else (GOOD, "HEALTHY")

# ======================= MASTHEAD =======================
st.markdown('<div class="kicker">IDT · Inclusivity · IIM Calcutta · Group 16, Section D</div>', unsafe_allow_html=True)
st.markdown(f'<div class="mast"><h1>Class Participation as a Site of Structural Exclusion</h1>'
            f'<div class="sub">Who the graded classroom rewards, and who it quietly costs. '
            f'Anonymous batch survey, N = {N}.</div></div>', unsafe_allow_html=True)
st.markdown('<div class="band"><b>How to read this:</b> &nbsp;'
            'green = healthy&nbsp; · &nbsp;amber = concern&nbsp; · &nbsp;red = needs action.'
            ' &nbsp; Charts are interactive: hover for exact counts.</div>', unsafe_allow_html=True)
st.write("")

c_fair, l_fair = signal(fair_hi, 35, 55, "low_bad")
c_gap, l_gap = signal(gap, 0.4, 0.8, "high_bad")
c_reh, l_reh = signal(pct_hi("rehearse"), 40, 65, "high_bad")
c_miss, l_miss = signal(missed_oftenish, 30, 45, "high_bad")

kpis = [
    (f"{fair_hi:.0f}%", "consider CP grading fair", c_fair, l_fair, f"{fair_lo:.0f}% actively disagree"),
    (f"+{gap:.2f}", "comfort jump, full section to small group (1-5)", c_gap, l_gap, "same people, lower exposure"),
    (f"{pct_hi('rehearse'):.0f}%", "rehearse before speaking", c_reh, l_reh, "the hidden preparation tax"),
    (f"{missed_oftenish:.0f}%", "often lose a ready point to a faster speaker", c_miss, l_miss, "airtime is scarce"),
]
for col, (num, lab, colr, tag, sub) in zip(st.columns(4), kpis):
    col.markdown(f'<div class="kpi" style="border-top-color:{colr}">'
                 f'<span class="tag" style="background:{colr}">{tag}</span>'
                 f'<div class="num" style="color:{colr};margin-top:8px">{num}</div>'
                 f'<div class="lab">{lab}</div>'
                 f'<div class="note" style="margin-top:6px;font-size:.72rem;color:{FAINT}">{sub}</div></div>',
                 unsafe_allow_html=True)

# ======================= ROW 1 =======================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="claim">The barrier is the graded plenary, not the student.</div>', unsafe_allow_html=True)
st.markdown('<div class="note">If the same people are far more willing to speak in a small group than in the full '
            'section, CP is measuring comfort with a high-exposure format, not command of the material.</div>', unsafe_allow_html=True)
st.write("")
a, b, c = st.columns(3)
with a:
    st.markdown(f'<div class="note"><b>Full section</b> · mean <span style="color:{c_gap}">{mean("full"):.2f}</span>/5</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("full", ["1 v.uncomf", "2", "3", "4", "5 v.comf"], True), use_container_width=True, config={"displayModeBar": False})
with b:
    st.markdown(f'<div class="note"><b>Small group / 1-to-1</b> · mean <span style="color:{GOOD}">{mean("small"):.2f}</span>/5</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("small", ["1 v.uncomf", "2", "3", "4", "5 v.comf"], True), use_container_width=True, config={"displayModeBar": False})
with c:
    st.markdown(f'<div class="note"><b>"CP grading is fair"</b> · mean <span style="color:{c_fair}">{mean("fair"):.2f}</span>/5</div>', unsafe_allow_html=True)
    st.plotly_chart(likert("fair", ["1 disagree", "2", "3", "4", "5 agree"], True), use_container_width=True, config={"displayModeBar": False})
st.markdown(f'<div class="note">Comfort rises <b style="color:{c_gap}">{gap:.2f} points</b> when the room shrinks. '
            f'On fairness, the red mass on the left is the story: <b style="color:{c_fair}">{fair_lo:.0f}%</b> actively '
            f'disagree that CP is fair, against {fair_hi:.0f}% who agree.</div>', unsafe_allow_html=True)

# ======================= ROW 2 =======================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="claim">Participation carries a hidden tax, and misreads capable students.</div>', unsafe_allow_html=True)
st.markdown('<div class="note">Most students rehearse before speaking, so spoken fluency is partly rehearsal capacity. '
            'And most say their written work represents them better, so the metric mismeasures known ability.</div>', unsafe_allow_html=True)
st.write("")
a, b = st.columns(2)
with a:
    st.markdown(f'<div class="note"><b>"I rehearse in my head before I speak."</b> · <span style="color:{c_reh}">{pct_hi("rehearse"):.0f}% agree</span></div>', unsafe_allow_html=True)
    st.plotly_chart(likert("rehearse", ["1 disagree", "2", "3", "4", "5 agree"], False), use_container_width=True, config={"displayModeBar": False})
with b:
    cw, _ = signal(pct_hi("written"), 40, 60, "high_bad")
    st.markdown(f'<div class="note"><b>"My written work reflects me better than my speaking."</b> · <span style="color:{cw}">{pct_hi("written"):.0f}% agree</span></div>', unsafe_allow_html=True)
    st.plotly_chart(likert("written", ["1 disagree", "2", "3", "4", "5 agree"], False), use_container_width=True, config={"displayModeBar": False})

# ======================= ROW 3 =======================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="claim">Airtime is scarce, contested, and unequally distributed.</div>', unsafe_allow_html=True)
st.write("")
a, b = st.columns(2)
with a:
    st.markdown('<div class="note"><b>"Had a point ready but did not get to say it."</b></div>', unsafe_allow_html=True)
    fig = go.Figure(go.Bar(x=mcount, y=morder, orientation="h", marker_color=[GOOD, GOOD, BAR_LT, WARN, CRIT],
                           text=mcount, textposition="outside", textfont=dict(size=13, color=INK), cliponaxis=False,
                           hovertemplate="%{y}: %{x} respondents<extra></extra>"))
    fig.update_layout(**base_layout(250))
    fig.update_xaxes(visible=False, range=[0, max(mcount) * 1.22])
    fig.update_yaxes(categoryorder="array", categoryarray=morder[::-1], tickfont=dict(size=11))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f'<div class="note"><b style="color:{CRIT}">{missed_oftenish:.0f}%</b> answered "often" or "very often".</div>', unsafe_allow_html=True)
with b:
    st.markdown(f'<div class="note"><b>Distribution of "voice" (Lorenz)</b> · Gini '
                f'<span style="color:{CRIT}">{gini_full:.2f}</span> full vs '
                f'<span style="color:{GOOD}">{gini_small:.2f}</span> small</div>', unsafe_allow_html=True)
    pf, cf = lorenz(arr("full")); ps, cs = lorenz(arr("small"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=FAINT, dash="dash", width=1.2), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ps, y=cs, mode="lines", line=dict(color=GOOD, width=2.4), hovertemplate="Small group<extra></extra>"))
    fig.add_trace(go.Scatter(x=pf, y=cf, mode="lines", line=dict(color=CRIT, width=2.6), hovertemplate="Full section<extra></extra>"))
    fig.update_layout(**base_layout(250))
    fig.update_xaxes(range=[0, 1], title=dict(text="share of students", font=dict(size=11)), tickfont=dict(size=10))
    fig.update_yaxes(range=[0, 1], title=dict(text="share of comfort", font=dict(size=11)), tickfont=dict(size=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="note">Further below the dashed equality line means more unequal. '
                'Voice concentrates more in the graded full section.</div>', unsafe_allow_html=True)

# ======================= ROW 4 =======================
st.markdown("<hr>", unsafe_allow_html=True)
a, b = st.columns([1.05, 1])
with a:
    st.markdown('<div class="sectitle">Who answered</div>', unsafe_allow_html=True)
    st.markdown('<div class="note">Sample composition. The comfort gap holds across these groups, which is why we read '
                'it as structural rather than a quirk of one background.</div>', unsafe_allow_html=True)
    st.write("")
    def compbar(d):
        keys = list(d.keys()); vals = list(d.values())
        fig = go.Figure(go.Bar(x=vals, y=keys, orientation="h", marker_color=BAR,
                               text=vals, textposition="outside", textfont=dict(size=12, color=INK), cliponaxis=False,
                               hovertemplate="%{y}: %{x}<extra></extra>"))
        fig.update_layout(**base_layout(150))
        fig.update_xaxes(visible=False, range=[0, max(vals) * 1.25])
        fig.update_yaxes(tickfont=dict(size=10.5), autorange="reversed")
        return fig
    st.markdown('<div class="note" style="margin-bottom:-6px"><b>Medium of schooling</b></div>', unsafe_allow_html=True)
    st.plotly_chart(compbar(DEMO_MEDIUM), use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="note" style="margin-bottom:-6px"><b>Work experience</b></div>', unsafe_allow_html=True)
    st.plotly_chart(compbar(DEMO_EXP), use_container_width=True, config={"displayModeBar": False})
with b:
    st.markdown('<div class="sectitle">What respondents said</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="note">Themes from the {N_OPEN} optional written responses, grouped and paraphrased '
                f'(individual responses are not reproduced). Tone lean is illustrative, not statistical, at this small n.</div>', unsafe_allow_html=True)
    st.write("")
    fig = go.Figure()
    for lab, val, colr in TONE:
        fig.add_trace(go.Bar(x=[val], y=["tone"], orientation="h", marker_color=colr,
                             text=[f"{lab} ({val})"], textposition="inside", insidetextanchor="middle",
                             textfont=dict(color="#fff", size=11), hovertemplate=f"{lab}: {val}<extra></extra>"))
    fig.update_layout(**base_layout(85), barmode="stack")
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    for head, colr, body in [
        ("Grade quality, not volume", CRIT, "Marks reward how often you speak, not the merit of the point; scoring should turn on quality."),
        ("Decouple from or reduce the grade", WARN, "The CP incentive drives performative, repetitive talk; lower it or reward it another way."),
        ("It wastes class time", WARN, "Desperate CP crowds out material the professor meant to cover, and turns discussion into competition."),
        ("Provide a written channel", GOOD, "Let students submit points in writing (a live in-class channel with hidden names, or a written note) that counts toward CP."),
    ]:
        st.markdown(f'<div style="border:1px solid {LINE};border-left:4px solid {colr};padding:9px 12px;margin-bottom:8px;">'
                    f'<div style="font-family:Georgia,serif;font-size:.98rem;">{head}</div>'
                    f'<div class="note" style="margin-top:2px">{body}</div></div>', unsafe_allow_html=True)

# ======================= FOOTER =======================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f'<div class="caveat"><b>About this data.</b> Indicative self-report survey, N = {N}, collected anonymously '
            '(no names or emails). It measures perceived comfort, effort and fairness, not actual CP grade records. '
            'The sample skews English-medium, engineering and early-career, so patterns are indicative, not conclusive. '
            'Scales run 1 to 5 with 5 as the most positive end. Figures shown are aggregate counts; open responses are '
            'paraphrased in aggregate and never reproduced verbatim.</div>', unsafe_allow_html=True)
st.write("")
st.markdown('<div class="band"><b>Interview audio &amp; transcripts (faculty, academic associate, students):</b> &nbsp;'
            '<a href="https://drive.google.com/drive/folders/1tYvQGRyM4vHBq0ppWRWvV5tAhG7LKQf2?usp=drive_link" target="_blank">'
            'shared Drive folder</a></div>', unsafe_allow_html=True)
st.markdown('<div class="note" style="margin-top:10px">IDT: Inclusivity group project · Group 16, Section D · IIM Calcutta '
            '· diagnosis and intervention detailed in the accompanying report and policy memo.</div>', unsafe_allow_html=True)
