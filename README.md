# SKUNIVO

**Explainable E-commerce Decision Intelligence**

SKUNIVO is a Streamlit decision-support MVP for merchandising teams. It
benchmarks marketplace listings within their local market context, creates a
transparent opportunity score, and explains which products should be protected,
tested, reviewed, maintained, or deprioritized.

The application uses 1,157 latest listings across 20 shops in Indonesia and
Vietnam. It consumes precomputed outputs and does not retrain models during app use.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Product boundary

This prototype prioritizes products using observed marketplace signals. It does
not estimate causal promotion lift or forecast transactional demand with the
current three-day snapshot dataset.

For architecture, deployment, limitations, troubleshooting, screenshots, and the
demo test script, see [README_MVP.md](README_MVP.md).
