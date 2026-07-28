# MerchPilot AI — Public MVP

## 1. Product overview

MerchPilot AI is an explainable e-commerce Decision Copilot. It helps merchandising
teams decide which product listings to protect, review, test, maintain, or
deprioritize. The application consumes precomputed outputs; it does not retrain a
model during normal use.

Primary promise: **Turn marketplace signals into explainable product decisions.**

Important boundary: this is a decision-support prototype. It does not forecast
transactional demand, estimate causal promotion lift, optimize profit or inventory,
calculate ROAS, automate pricing, or guarantee outcomes.

## 2. Main features

- Premium landing experience with a real recommendation preview
- Executive portfolio overview with normalized market views
- Product prioritization with market, shop, category, decision, confidence, score,
  promotion, official-shop, engagement, and local-price filters
- Auditable product explanations with peer percentiles and business-language reasons
- Transparent six-component what-if score simulator
- Methodology, model diagnostics, robustness, limitations, and data roadmap
- Structured usability feedback with local append or public-session download
- Seven-page in-app navigation and a five-task guided evaluation flow

## 3. Project structure

```text
app.py                         Streamlit entry point and seven page views
app_components/
  data_loader.py               Cached loading, aliases, schema validation
  filters.py                   Filter, sort, active-review, price-label logic
  charts.py                    Chart helpers and normalized summaries
  recommendation_ui.py         Score formula, presets, tiers, guidance
  feedback.py                  Validation and append/session export behavior
  styles.py                    Brand and responsive application styling
outputs/                       Precomputed recommendation and evaluation files
outputs/charts/                High-resolution chart assets
.streamlit/config.toml         Public-safe Streamlit configuration
.streamlit/secrets.toml.example Optional secret template; contains no credentials
tests/test_mvp.py              Formula, data, filter, and append tests
```

The app resolves every data path relative to `app.py`; no local absolute path is
required at runtime.

## 4. Local installation

Python 3.11 or 3.12 is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS or Linux, activate with:

```bash
source .venv/bin/activate
```

## 5. Local run instructions

From the project root:

```powershell
streamlit run app.py
```

The local app opens at the URL printed by Streamlit, normally
`http://localhost:8501`.

To validate the core decision logic:

```powershell
python -m unittest tests.test_mvp -v
```

## 6. Public deployment instructions

The repository is ready for Streamlit Community Cloud.

1. Create a Git repository and include `app.py`, `app_components/`,
   `requirements.txt`, `.streamlit/config.toml`, the required `outputs/*.csv`
   files, and `outputs/charts/*.png`.
2. Push the repository to GitHub.
3. In Streamlit Community Cloud, choose **Create app**.
4. Select the repository and branch, then set **Main file path** to `app.py`.
5. Add `MERCHPILOT_PUBLIC_MODE=true` in the app settings if you want the
   feedback screen to explicitly use session/download mode.
6. Deploy and confirm all seven pages, charts, downloads, and product selectors.

Exact first-push commands (replace the placeholder; do not commit secrets):

```powershell
git init
git add .
git commit -m "Build MerchPilot AI public MVP"
git branch -M main
git remote add origin <REPOSITORY_URL>
git push -u origin main
```

## 7. Data limitations

- 1,157 latest listings across 20 shops and two markets
- Three snapshot dates only: 2026-07-01 to 2026-07-03
- Engagement measures are cumulative
- No orders, customers, cost, inventory history, ad spend, realized revenue,
  experimental treatment/control, or currency metadata
- Shop-category coverage is 66.1%; missing mappings display as unavailable
- Indonesia and Vietnam prices remain in local units and are never directly compared
- The actionable Indonesia ML benchmark is useful; Vietnam ranking quality is limited
- The descriptive ML experiment includes historical sold value and is leakage-prone

## 8. Feedback persistence note

Local development appends valid rows to `outputs/mvp_user_feedback.csv`; existing
rows are never overwritten. The file is ignored by Git.

Streamlit Community Cloud local files are not durable. With no external storage,
public submissions remain in the current session and are offered as a CSV download.
Personal details are optional. A future external persistence integration should use
Streamlit secrets or environment variables—never hard-coded credentials.

## 9. Troubleshooting

- **Missing output message:** confirm the required CSVs and eight PNG charts are
  present under `outputs/`.
- **Schema validation message:** regenerate the precomputed decision outputs or
  compare column names with `app_components/data_loader.py`. Reasonable aliases are
  supported centrally.
- **Charts do not render:** confirm Git LFS did not replace PNGs with pointer files.
- **No price filter:** select exactly one country; this is an intentional
  cross-currency safeguard.
- **Feedback is temporary:** set up durable external storage or export the submitted
  row from the public-session screen.
- **Port already in use:** run `streamlit run app.py --server.port 8502`.

## 10. Screenshot placeholders

Capture these after deployment and replace the placeholders in project materials:

- `[Screenshot: premium Home hero and real recommendation preview]`
- `[Screenshot: Executive Overview with normalized market selector]`
- `[Screenshot: Product Prioritization filters and ranked table]`
- `[Screenshot: one Product Explanation decision record]`
- `[Screenshot: What-if Score Explorer with contribution chart]`
- `[Screenshot: Methodology model results and limitations]`
- `[Screenshot: User Feedback form and persistence notice]`

## 11. Demo testing script

1. Open **Home** and read the product promise and honest boundary.
2. Select **Launch Decision Copilot**.
3. Filter to one country, one shop, and an active-review recommendation.
4. Confirm the local currency label and download the filtered CSV.
5. Open one product explanation and compare its score, confidence, peer benchmarks,
   and three reasons.
6. Download the product decision summary.
7. Open **What-if Score Explorer**, choose each preset, and move one component from
   0 to 100.
8. Confirm all-zero components score 0, all-100 score 100, and all-50 score 50.
9. Review Indonesia and Vietnam model notes under **Methodology and Transparency**.
10. Submit the feedback form without personal details and download the resulting row.
