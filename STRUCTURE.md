# Project Structure

```
canai-cafe-team-a/
├── data/
│   ├── raw/                        # Original dataset — drop file here, never edit
│   └── clean/                      # Cleaned output from notebook 01 (data_clean.csv)
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb      # Member A — cleans raw data
│   ├── 02_eda_insights.ipynb       # Member B — analysis and business insights
│   └── 03_forecasting_model.ipynb  # Member C — forecasting model and 6-month projection
│
├── outputs/
│   ├── charts/                     # Exported charts from notebooks 02 and 03
│   └── forecast_results.csv        # Forecast output from notebook 03 — imported into Power BI
│
├── dashboard/                      # Power BI .pbix file (Member D)
├── presentation/                   # Final slide deck
│
├── docs/
│   └── data_cleaning_summary.md    # Member A — documents all cleaning decisions
│
├── requirements.txt                # Python dependencies
├── README.md                       # Setup instructions
├── Plan.md                         # Project plan and schedule
├── CONTRIBUTING.md                 # Branching and git workflow
└── STRUCTURE.md                    # This file
```

---

## Notebook Dependency Order

Notebooks must be run in order — each one depends on the output of the previous:

```
01_data_cleaning.ipynb
  └── produces data/clean/data_clean.csv
        ├── used by 02_eda_insights.ipynb
        └── used by 03_forecasting_model.ipynb
              └── produces outputs/forecast_results.csv
                    └── imported into dashboard/
```

Member A should complete and share `data_clean.csv` before Members B and C begin their notebooks.

---

## Key Output Files

| File | Produced by | Consumed by |
|------|-------------|-------------|
| `data/clean/data_clean.csv` | Notebook 01 | Notebooks 02, 03 |
| `outputs/forecast_results.csv` | Notebook 03 | Power BI dashboard |
| `docs/data_cleaning_summary.md` | Member A | Presentation slides |
