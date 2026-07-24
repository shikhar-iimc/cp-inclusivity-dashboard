# Class Participation as a Site of Structural Exclusion — Survey Dashboard
IDT: Inclusivity group project · Group 16, Section D · IIM Calcutta

Interactive dashboard of anonymous survey findings (N = 50) on how graded
Class Participation is experienced.

## Privacy
No response-level data is stored in this repository. All figures are embedded
as **aggregate counts** inside `app.py` (the COUNTS / DEMO dictionaries).
No names or emails were collected in the survey.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Update the numbers
Edit the `COUNTS`, `MISSED`, `DEMO_MEDIUM`, `DEMO_EXP`, `TONE` and `N`
values at the top of `app.py`, then redeploy. No data file needed.

## Deploy
Streamlit Community Cloud, entry point `app.py`. The `.streamlit/config.toml`
forces a light theme so the dashboard renders identically regardless of the
viewer's browser theme.
