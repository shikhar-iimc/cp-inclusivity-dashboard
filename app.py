"""
Class Participation as a Site of Structural Exclusion
IDT: Inclusivity — Group Project, IIM Calcutta
Survey dashboard (N = 49). Aggregate, anonymised, self-report data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import streamlit as st

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="CP as Structural Exclusion — Survey Dashboard",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------
# MONOCHROME STYLING
# ----------------------------------------------------------------------
INK = "#111111"
MID = "#666666"
LINE = "#DDDDDD"
FILL = "#111111"
FILL_MUTED = "#BBBBBB"

st.markdown(
    """
    <style>
      /* base */
      .stApp { background:#FFFFFF; }
      html, body, [class*="css"] { color:#111111; }
      .block-container { max-width: 1080px; padding-top: 2.2rem; padding-bottom: 4rem; }

      /* typography */
      h1,h2,h3 { font-family: Georgia,'Times New Roman',serif !important; color:#111 !important; letter-spacing:-.2px; }
      p,li,div,span,label { font-family: -apple-system,Segoe UI,Helvetica,Arial,sans-serif; }

      .masthead { border-bottom:2px solid #111; padding-bottom:14px; margin-bottom:6px; }
      .masthead h1 { font-size:2.05rem; margin:0 0 4px 0; }
      .kicker { font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif !important;
                text-transform:uppercase; letter-spacing:2.5px; font-size:.72rem; color:#666; margin-bottom:10px; }
      .sub { color:#444; font-size:.98rem; margin-top:2px; }

      .claim { border-left:3px solid #111; padding:6px 0 6px 14px; margin:8px 0 4px 0;
               font-family:Georgia,serif; font-size:1.18rem; color:#111; }
      .note { color:#666; font-size:.9rem; }

      .kpi { border:1px solid #DDD; padding:18px 16px; height:100%; }
      .kpi .num { font-family:Georgia,serif; font-size:2.3rem; line-height:1; color:#111; }
      .kpi .lab { font-size:.82rem; color:#555; margin-top:8px; line-height:1.3; }

      .caveat { border:1px solid #111; background:#FAFAFA; padding:12px 16px; font-size:.85rem; color:#333; }
      .sectionrule { border:0; border-top:1px solid #DDD; margin:34px 0 6px 0; }

      hr { border:0; border-top:1px solid #DDD; }
      .stMarkdown a { color:#111; }
      /* hide default streamlit chrome */
      #MainMenu, footer, header { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# DATA  (aggregate counts from the section survey, N = 49)
# Scales 1–5 where 5 = most comfortable / strongest agreement.
# Reconstruct per-respondent arrays from counts for exact stats.
# ----------------------------------------------------------------------
N = 49
COUNTS = {
    "full":     {1: 6, 2: 6, 3: 17, 4: 11, 5: 9},   # comfort speaking in FULL section
    "small":    {1: 1, 2: 3, 3: 7,  4: 18, 5: 20},  # comfort in SMALL group / 1-1
    "rehearse": {1: 3, 2: 3, 3: 8,  4: 20, 5: 15},  # rehearse before speaking
    "written":  {1: 1, 2: 2, 3: 14, 4: 16, 5: 16},  # written reflects me better
    "fair":     {1: 15, 2: 8, 3: 13, 4: 10, 5: 3},  # CP grading is fair
}
MISSED = {"Never": 3, "Rarely": 3, "Sometimes": 18, "Often": 18, "Very often": 7}

def arr(key):
    out = []
    for k, v in COUNTS[key].items():
        out += [k] * v
    return np.array(out, dtype=float)

def mean(key):
    return arr(key).mean()

def pct_agree(key):           # % rating 4 or 5
    a = arr(key)
    return (a >= 4).mean() * 100

def gini(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    c = np.cumsum(x)
    return (n + 1 - 2 * np.sum(c) / c[-1]) / n

def lorenz(x):
    x = np.sort(np.asarray(x, float))
    c = np.insert(np.cumsum(x), 0, 0)
    c = c / c[-1]
    p = np.linspace(0, 1, len(c))
    return p, c

gap = mean("small") - mean("full")
missed_oftenish = (MISSED["Often"] + MISSED["Very often"]) / N * 100
fair_pct = pct_agree("fair")
gini_full = gini(arr("full"))
gini_small = gini(arr("small"))

# ----------------------------------------------------------------------
# SHARED MATPLOTLIB STYLE (monochrome, minimal)
# ----------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Georgia", "Times New Roman", "DejaVu Serif"],
    "axes.edgecolor": INK,
    "axes.linewidth": 0.8,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

def clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=0)

def likert_fig(key, labels=("1", "2", "3", "4", "5"), highlight_high=True):
    a = COUNTS[key]
    vals = [a.get(i, 0) for i in range(1, 6)]
    fig, ax = plt.subplots(figsize=(4.6, 2.5), dpi=150)
    colors = [FILL_MUTED, FILL_MUTED, FILL_MUTED, FILL, FILL] if highlight_high else [FILL] * 5
    ax.bar(range(1, 6), vals, color=colors, width=0.72, zorder=3)
    for i, v in zip(range(1, 6), vals):
        if v:
            ax.text(i, v + 0.3, str(v), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticks([])
    ax.set_ylim(0, max(vals) * 1.25)
    clean(ax)
    ax.spines["left"].set_visible(False)
    fig.tight_layout()
    return fig

# ----------------------------------------------------------------------
# MASTHEAD
# ----------------------------------------------------------------------
st.markdown('<div class="kicker">IDT · Inclusivity — IIM Calcutta (Group 16, Section D) </div>', unsafe_allow_html=True)
st.markdown(
    '<div class="masthead"><h1>Class Participation as a Site of Structural Exclusion</h1>'
    '<div class="sub">A section survey on who the graded classroom rewards — and who it quietly costs. '
    f'Self-reported responses, N = {N}.</div></div>',
    unsafe_allow_html=True,
)
st.write("")

# KPI ROW
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi"><div class="num">+{gap:.2f}</div>'
                '<div class="lab">Comfort rises from full-section to small-group speaking (1–5 scale)</div></div>',
                unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi"><div class="num">{fair_pct:.0f}%</div>'
                '<div class="lab">Agree the CP grading system, as it works now, is fair</div></div>',
                unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi"><div class="num">{pct_agree("rehearse"):.0f}%</div>'
                '<div class="lab">Rehearse in their head before speaking in class</div></div>',
                unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi"><div class="num">{missed_oftenish:.0f}%</div>'
                '<div class="lab">Often or very often lost a ready point to a faster speaker</div></div>',
                unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PANEL 1 — THE COMFORT GAP
# ----------------------------------------------------------------------
st.markdown('<hr class="sectionrule">', unsafe_allow_html=True)
st.markdown('<div class="claim">The barrier is the graded plenary, not the student.</div>', unsafe_allow_html=True)
st.markdown('<div class="note">Supports the redesign\'s core premise. If the same people are markedly more '
            'willing to speak in a small group than in the full section, what CP measures is comfort with a '
            'high-exposure format — a disposition — not understanding of the material.</div>', unsafe_allow_html=True)
st.write("")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Comfort — FULL section** &nbsp; <span class='note'>mean "
                f"{mean('full'):.2f} / 5</span>", unsafe_allow_html=True)
    st.pyplot(likert_fig("full", ("1\nvery\nuncomf.", "2", "3", "4", "5\nvery\ncomf.")))
with c2:
    st.markdown("**Comfort — SMALL group / one-to-one** &nbsp; <span class='note'>mean "
                f"{mean('small'):.2f} / 5</span>", unsafe_allow_html=True)
    st.pyplot(likert_fig("small", ("1\nvery\nuncomf.", "2", "3", "4", "5\nvery\ncomf.")))
st.markdown(f'<div class="note">The distribution shifts right by <b>{gap:.2f} points</b> when the room shrinks '
            '— the same respondents, a different setting.</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PANEL 2 — LEGITIMACY
# ----------------------------------------------------------------------
st.markdown('<hr class="sectionrule">', unsafe_allow_html=True)
st.markdown('<div class="claim">The metric has lost the room.</div>', unsafe_allow_html=True)
st.markdown('<div class="note">Establishes urgency. A grading instrument that fewer than a third of those graded '
            'consider fair has a legitimacy problem, independent of any single student\'s experience.</div>',
            unsafe_allow_html=True)
st.write("")
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown('**"CP grading, as it works now, is fair."** &nbsp; <span class="note">mean '
                f"{mean('fair'):.2f} / 5</span>", unsafe_allow_html=True)
    st.pyplot(likert_fig("fair", ("1\nstrongly\ndisagree", "2", "3", "4", "5\nstrongly\nagree"),
                         highlight_high=False))
with c2:
    st.write("")
    st.markdown(
        f'<div style="border:1px solid #DDD;padding:20px;">'
        f'<div style="font-family:Georgia,serif;font-size:2.6rem;line-height:1;">{fair_pct:.0f}%</div>'
        '<div class="note" style="margin-top:6px;">agree or strongly agree it is fair '
        f'({COUNTS["fair"][4] + COUNTS["fair"][5]} of {N}).</div>'
        f'<div style="font-family:Georgia,serif;font-size:2.6rem;line-height:1;margin-top:16px;">'
        f'{(COUNTS["fair"][1] + COUNTS["fair"][2]) / N * 100:.0f}%</div>'
        '<div class="note" style="margin-top:6px;">actively disagree '
        f'({COUNTS["fair"][1] + COUNTS["fair"][2]} of {N}).</div></div>',
        unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PANEL 3 — THE HIDDEN TAX
# ----------------------------------------------------------------------
st.markdown('<hr class="sectionrule">', unsafe_allow_html=True)
st.markdown('<div class="claim">Participation carries a hidden preparation tax — and misreads capable students.</div>',
            unsafe_allow_html=True)
st.markdown('<div class="note">Supports two design moves: an insight-weighted rubric, and a written / '
            'submit-in-advance contribution channel. If most students rehearse before speaking, spoken fluency is '
            'partly rehearsal capacity; if most feel their written work represents them better, the metric is '
            'mismeasuring known ability.</div>', unsafe_allow_html=True)
st.write("")
c1, c2 = st.columns(2)
with c1:
    st.markdown('**"I rehearse in my head before I speak."** &nbsp; <span class="note">'
                f"{pct_agree('rehearse'):.0f}% agree · mean {mean('rehearse'):.2f}</span>", unsafe_allow_html=True)
    st.pyplot(likert_fig("rehearse", ("1\ndisagree", "2", "3", "4", "5\nagree")))
with c2:
    st.markdown('**"My written work reflects what I know better than my speaking."** &nbsp; <span class="note">'
                f"{pct_agree('written'):.0f}% agree · mean {mean('written'):.2f}</span>", unsafe_allow_html=True)
    st.pyplot(likert_fig("written", ("1\ndisagree", "2", "3", "4", "5\nagree")))

# ----------------------------------------------------------------------
# PANEL 4 — AIRTIME SCARCITY + LORENZ
# ----------------------------------------------------------------------
st.markdown('<hr class="sectionrule">', unsafe_allow_html=True)
st.markdown('<div class="claim">Airtime is scarce, contested, and unequally distributed.</div>', unsafe_allow_html=True)
st.markdown('<div class="note">Supports structured turn-taking and a cold-call / speaking-order roster. Half the '
            'room routinely loses a ready point to a faster speaker, and "voice" is more unequally distributed in '
            'the full section than in low-stakes settings.</div>', unsafe_allow_html=True)
st.write("")
c1, c2 = st.columns(2)
with c1:
    st.markdown('**"Had a point ready but did not get to say it."**')
    order = ["Never", "Rarely", "Sometimes", "Often", "Very often"]
    vals = [MISSED[k] for k in order]
    cols = [FILL_MUTED, FILL_MUTED, FILL_MUTED, FILL, FILL]
    fig, ax = plt.subplots(figsize=(4.6, 2.6), dpi=150)
    ax.barh(range(len(order)), vals, color=cols, zorder=3)
    for i, v in enumerate(vals):
        if v:
            ax.text(v + 0.3, i, str(v), va="center", fontsize=9)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=9)
    ax.invert_yaxis()
    ax.set_xticks([])
    clean(ax)
    ax.spines["bottom"].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    st.markdown(f'<div class="note"><b>{missed_oftenish:.0f}%</b> answered "often" or "very often".</div>',
                unsafe_allow_html=True)
with c2:
    st.markdown('**Lorenz curve — distribution of "voice"** &nbsp; <span class="note">'
                f"Gini {gini_full:.3f} (full) vs {gini_small:.3f} (small group)</span>", unsafe_allow_html=True)
    pf, cf = lorenz(arr("full"))
    ps, cs = lorenz(arr("small"))
    fig, ax = plt.subplots(figsize=(4.6, 2.9), dpi=150)
    ax.plot([0, 1], [0, 1], color=MID, lw=0.9, ls=(0, (4, 3)), zorder=2)
    ax.plot(pf, cf, color=FILL, lw=2.0, zorder=4, label=f"Full section (Gini {gini_full:.2f})")
    ax.plot(ps, cs, color=FILL_MUTED, lw=2.0, zorder=3, label=f"Small group (Gini {gini_small:.2f})")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("cumulative share of students", fontsize=8)
    ax.set_ylabel("cumulative share of comfort", fontsize=8)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    clean(ax)
    fig.tight_layout()
    st.pyplot(fig)
    st.markdown('<div class="note">Further from the diagonal = more unequal. Voice concentrates more in the '
                'graded full section than in the small group.</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PANEL 5 — WHAT RESPONDENTS PROPOSED (paraphrased themes, no verbatim quotes)
# ----------------------------------------------------------------------
st.markdown('<hr class="sectionrule">', unsafe_allow_html=True)
st.markdown('<div class="claim">The redesign is not imposed — respondents asked for it.</div>', unsafe_allow_html=True)
st.markdown('<div class="note">Recurring themes from the optional open-response field, grouped and paraphrased '
            '(no individual responses are reproduced). The interventions below emerged from the affected group '
            'itself.</div>', unsafe_allow_html=True)
st.write("")
themes = [
    ("Grade quality, not frequency",
     "A recurring view held that marks reward volume of speaking over the merit of the point, and that scoring "
     "should turn on the quality of a contribution."),
    ("Provide a written / typed channel",
     "Several suggested a way to submit points in writing — a live in-class text channel or an email window "
     "shortly after class — for those who do not secure airtime."),
    ("Reduce or decouple the incentive",
     "A number of responses argued the CP weight drives performative, repetitive contributions that consume class "
     "time, and that the incentive should be lowered or separated from grades."),
    ("Structure who speaks and when",
     "Some pointed to formats that allocate speaking turns or a known order as fairer than a scramble for the floor."),
]
cA, cB = st.columns(2)
for i, (head, para) in enumerate(themes):
    with (cA if i % 2 == 0 else cB):
        st.markdown(
            f'<div style="border:1px solid #DDD;padding:16px;margin-bottom:16px;min-height:150px;">'
            f'<div style="font-family:Georgia,serif;font-size:1.05rem;margin-bottom:6px;">{head}</div>'
            f'<div class="note">{para}</div></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CAVEAT
# ----------------------------------------------------------------------
st.markdown('<hr class="sectionrule">', unsafe_allow_html=True)
st.markdown(
    f'<div class="caveat"><b>About this data.</b> Indicative self-report survey, N = {N}, collected anonymously '
    '(no names or emails). It measures perceived comfort, effort and fairness — not actual CP grade records. '
    'The sample skews English-medium, engineering, and early-career, so it is not representative of the batch on '
    'background; read the patterns as indicative, not conclusive. Scales run 1–5 with 5 as the most positive end. '
    'Open responses are paraphrased in aggregate and never reproduced verbatim.</div>',
    unsafe_allow_html=True)
st.write("")
st.markdown('<div class="note">IDT: Inclusivity group project · Survey instrument and diagnosis available in the '
            'accompanying report and artefact.</div>', unsafe_allow_html=True)
