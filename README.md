# Class Participation as a Site of Structural Exclusion — Survey Dashboard

Interactive dashboard for the IDT: Inclusivity group project (IIM Calcutta).
Presents aggregate, anonymised findings from a section survey (N = 49) on how
graded class participation is experienced.

## What it shows
1. **The comfort gap** — full-section vs small-group speaking comfort.
2. **Legitimacy** — how few students consider CP grading fair.
3. **The hidden tax** — rehearsal burden and written-vs-spoken mismatch.
4. **Airtime scarcity** — lost points and the Lorenz/Gini of "voice".
5. **What respondents proposed** — paraphrased open-response themes (no verbatim quotes).

## Data & ethics
Self-report survey, collected anonymously (no names or emails). Figures are
aggregate only; open-text responses are paraphrased in aggregate and never
reproduced verbatim. Data is indicative, not conclusive — the sample skews
English-medium, engineering, and early-career.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Hosted on Streamlit Community Cloud from this repository (`app.py` as the entry point).
