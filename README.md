# CanAI Café — Team A

Hackathon project: sales analysis, forecasting, and Power BI dashboard for CanAI Café.

---

## Project Structure

```
canai-cafe-team-a/
├── data/
│   ├── raw/                  # Drop the original dataset here (do not modify)
│   └── clean/                # Output of notebook 01 — data_clean.csv
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda_insights.ipynb
│   └── 03_forecasting_model.ipynb
├── outputs/
│   ├── charts/               # Exported charts from notebooks 02 and 03
│   └── forecast_results.csv  # Output of notebook 03 — imported into Power BI
├── dashboard/                # Power BI .pbix file
├── presentation/             # Final slide deck
├── docs/
│   └── data_cleaning_summary.md
├── requirements.txt
├── README.md
├── Plan.md
├── CONTRIBUTING.md
└── STRUCTURE.md
```

---

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd canai-cafe-team-a

# 2. Create and activate a virtual environment
python -m venv venv

# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add the raw dataset
# Copy the transaction CSV into data/raw/

# 5. Start Jupyter
jupyter notebook
```

> To deactivate the virtual environment when done, run `deactivate`.

---

## Notebooks

| Notebook | Owner | Purpose |
|----------|-------|---------|
| `01_data_cleaning.ipynb` | Member A | Clean raw data → `data/clean/data_clean.csv` |
| `02_eda_insights.ipynb` | Member B | EDA, trends, business insights |
| `03_forecasting_model.ipynb` | Member C | Train model, generate `outputs/forecast_results.csv` |

---

## Key Docs

- `Plan.md` — full project plan and schedule
- `CONTRIBUTING.md` — branching and git workflow
- `docs/data_cleaning_summary.md` — cleaning decisions log
