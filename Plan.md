# CanAI Café — Hackathon Plan

**Team:** 4 members | **Duration:** 2 days

---

## Final Deliverables

| # | Deliverable | Owner | Due |
|---|-------------|-------|-----|
| 1 | Clean dataset + Data Cleaning Summary doc | Member A | Day 1 EOD |
| 2 | Analytical Insights report | Member B | Day 2 noon |
| 3 | Forecasting / ML model + 6-month forecast | Member C | Day 2 noon |
| 4 | Interactive Power BI Dashboard | Member D | Day 2 noon |
| 5 | Presentation deck | All (lead: Member B) | Day 2 EOD |

---

## Role Assignment

| Member | Track | Responsibilities |
|--------|-------|-----------------|
| A | Data Engineering | Data assessment, cleaning, documentation |
| B | Analytics | EDA, insights, business recommendations, slide lead |
| C | Modeling | Feature engineering, forecasting model, evaluation |
| D | BI / Visualization | Power BI dashboard, data model, visuals |

> Everyone contributes slides for their own section. After Phase 1, Member A shifts to support B or C depending on bottlenecks.

---

## Phase 1 — Project Setup & Data Assessment
**All 4 members | Day 1 · 9:00–10:30 AM**

The goal of this phase is to collectively understand the data before splitting into parallel tracks. Decisions made here unblock everyone else.

### Tasks
- [ ] Set up shared folder structure and version control for notebooks, outputs, and docs
- [ ] Load raw dataset — inspect shape, column names, data types
- [ ] Generate a quick profile report (e.g. `pandas-profiling` / `ydata-profiling`) to get a fast overview
- [ ] As a team, agree on:
  - The primary date/time column and grain of analysis (daily? per-transaction?)
  - Definition of "sales" (revenue column, unit column, or both)
  - Which columns are critical vs. auxiliary
  - Handling strategy defaults (e.g. impute median vs. drop rows)
- [ ] Member A takes ownership of cleaning from here; others proceed to their tracks

---

## Phase 2 — Data Cleaning & Quality Documentation
**Member A (primary) | Day 1 · 10:30 AM – 3:00 PM**

Deliver: `data_clean.csv` + `Data_Cleaning_Summary.pdf/docx`

### Tasks

**Assessment**
- [ ] Audit every column for: null rate, unique values, min/max, format consistency
- [ ] Catalogue all issues found in a working notes table (column, issue type, count, severity)

**Cleaning — execute and document each decision**
- [ ] Missing values — decide per column: impute (mean/median/mode/forward-fill) or drop; record reason
- [ ] Duplicates — identify exact and near-duplicates; drop with justification
- [ ] Incorrect / invalid entries — negative quantities, future dates, impossible prices; correct or remove
- [ ] Inconsistent formats — standardise date formats, location names, product category labels, currency
- [ ] Outliers — use IQR or z-score; flag or cap outliers rather than silently dropping
- [ ] Save final clean file with a clear name and record row/column counts before vs. after

**Cleaning Summary Document**
- [ ] Table: issue found → cleaning action → rationale → rows affected
- [ ] Before/after statistics (record count, null counts, key column distributions)
- [ ] Any known remaining caveats or data limitations

> Once `data_clean.csv` is ready (target: 3:00 PM), share it immediately so Members B, C, and D can load it.

---

## Phase 3 — Exploratory Analysis & Business Insights
**Member B | Day 1 · 10:30 AM – Day 2 · 11:00 AM**

Deliver: `Analytical_Insights.pdf/docx` (feeds slides and dashboard recommendations panel)

### Tasks

**Sales Trend Analysis**
- [ ] Revenue and transaction volume over time — daily, weekly, monthly aggregations
- [ ] Month-over-month and year-over-year growth rates
- [ ] Identify peak periods, slow seasons, and any anomalies

**Regional Performance**
- [ ] Revenue, volume, and average transaction value per location
- [ ] Rank locations by performance; flag underperformers
- [ ] Regional growth trends over the year

**Product / Category Performance**
- [ ] Top 10 and bottom 10 products by revenue and units sold
- [ ] Category-level breakdown and share of total sales
- [ ] Products with declining vs. growing sales trajectory

**Business Insight Synthesis**
- [ ] Identify at minimum 3 concrete, data-backed business opportunities or risks
- [ ] Write each insight as: *finding → evidence → recommended action*
- [ ] Export key charts/tables for use in dashboard and slides

---

## Phase 4 — Forecasting Model
**Member C | Day 1 · 10:30 AM – Day 2 · 11:00 AM**

Deliver: `forecast_results.csv` (6-month projections) + model documentation section for slides

### Tasks

**Preparation**
- [ ] Aggregate clean data to the required time series grain (daily or monthly total sales)
- [ ] Perform stationarity check and decompose series (trend, seasonality, residual)
- [ ] Engineer features if using ML: lag features, rolling averages, month/quarter indicators

**Model Selection & Training**
- [ ] Evaluate 2–3 candidate approaches (e.g. Prophet, SARIMA, or XGBoost regressor) and pick one
- [ ] Document why this model fits the data characteristics (seasonality present? limited history?)
- [ ] Train on 80% of historical data; hold out last 20% for validation

**Evaluation**
- [ ] Compute MAE, RMSE, and MAPE on the validation set
- [ ] Plot actual vs. predicted on the holdout period to visually confirm fit

**Forecast**
- [ ] Generate monthly sales forecast for the next 6 months with confidence intervals
- [ ] Export `forecast_results.csv`: columns — `month`, `forecasted_revenue`, `lower_bound`, `upper_bound`
- [ ] Write a short model card: model chosen, assumptions, metrics, known limitations

> Share `forecast_results.csv` with Member D by Day 2 · 11:00 AM so it can be imported into the dashboard.

---

## Phase 5 — Power BI Dashboard
**Member D | Day 1 · 10:30 AM – Day 2 · 11:00 AM**

Deliver: Published Power BI `.pbix` file with 5 report pages

### Setup (Day 1 PM)
- [ ] Connect Power BI to `data_clean.csv`
- [ ] Build data model — define date table, relationships, key measures (Total Revenue, Avg Transaction Value, Units Sold)
- [ ] Set up DAX measures needed across all pages
- [ ] Apply CanAI Café branding: colour palette, logo placement, consistent font

### Report Pages

**Page 1 — Sales Overview**
- [ ] Revenue and transaction volume trend line over full year
- [ ] KPI cards: Total Revenue, Total Transactions, Avg Order Value
- [ ] Slicers: date range, region, product category

**Page 2 — Regional Performance**
- [ ] Map visual or bar chart comparing locations by revenue
- [ ] Table: location, revenue, volume, growth %, rank

**Page 3 — Product Performance**
- [ ] Bar chart: top/bottom 10 products by revenue
- [ ] Category breakdown donut or treemap
- [ ] Trend sparklines per top category

**Page 4 — Sales Forecast**
- [ ] Import `forecast_results.csv` once Member C delivers it
- [ ] Line chart: historical actuals + 6-month forecast with confidence band
- [ ] KPI card: projected 6-month revenue total

**Page 5 — Business Recommendations**
- [ ] Text / card visuals summarising the 3+ insights from Member B
- [ ] Supporting charts that reinforce each recommendation

### QA
- [ ] All slicers cross-filter correctly across pages
- [ ] No broken visuals or DAX errors
- [ ] Readable on a standard laptop screen

---

## Phase 6 — Presentation Deck
**Lead: Member B | All contribute | Day 2 · 11:00 AM – EOD**

Target: 10–12 slides, ~10-minute presentation

### Slide Structure

| Slide | Title | Owner |
|-------|-------|-------|
| 1 | Title slide — CanAI Café Analytics | All |
| 2 | Problem Statement & Objectives | B |
| 3 | Data Overview — source, volume, year covered | A |
| 4 | Data Quality Challenges & Cleaning Approach | A |
| 5 | Key Insight 1 — Sales Trends | B |
| 6 | Key Insight 2 — Regional & Product Performance | B |
| 7 | Key Insight 3 — Opportunities & Risks | B |
| 8 | Forecasting Model — method, metrics, results | C |
| 9 | 6-Month Forecast & Projections | C |
| 10 | Dashboard Demo (screenshots or live) | D |
| 11 | Business Recommendations | B |
| 12 | Conclusion & Next Steps | All |

### Tasks
- [ ] Each member drafts their slides by Day 2 · 1:00 PM
- [ ] Member B assembles into one deck and applies consistent template by 2:00 PM
- [ ] Full team reviews and edits by 3:00 PM
- [ ] Practice run-through at least once before submission

---

## Day-by-Day Schedule

### Day 1

| Time | Member A | Member B | Member C | Member D |
|------|----------|----------|----------|----------|
| 9:00–10:30 | **All together** — data load, profiling, team decisions | | | |
| 10:30–1:00 | Data cleaning (missing values, duplicates) | EDA — time trends | Model selection, data prep for TS | PBI setup, data model, DAX measures |
| 1:00–3:00 | Data cleaning (formats, outliers) | Regional & product analysis | Model training + validation | Sales Overview & Regional pages |
| 3:00–5:00 | Finalize `data_clean.csv`, write cleaning summary doc | Start insights doc | Tune model, begin forecast generation | Product Performance page |
| EOD | **Share `data_clean.csv` with team** | Draft 3 key insights | Share preliminary model metrics | Demo PBI pages 1–3 to team |

### Day 2

| Time | Member A | Member B | Member C | Member D |
|------|----------|----------|----------|----------|
| 9:00–11:00 | Support B or C on blockers | Finalize insights doc | Finalize forecast, export `forecast_results.csv` | Forecast & Recommendations pages |
| 11:00–1:00 | Draft slides 3–4 | Draft slides 5–7, 11 | Draft slides 8–9 | Draft slide 10, QA dashboard |
| 1:00–3:00 | **All** — assemble full deck, peer review | | | |
| 3:00–4:00 | **All** — practice presentation run-through | | | |
| 4:00–EOD | **All** — final polish, submission | | | |

---

## Dependencies & Critical Path

```
Raw Data
  └─► Phase 1 (Setup + Assessment) ──► data_clean.csv
                                             │
                        ┌────────────────────┼──────────────────────┐
                        ▼                    ▼                      ▼
                   Phase 3 (EDA)      Phase 4 (Model)        Phase 5 (PBI)
                        │                    │                      │
                        └────────────────────┼──────────────────────┘
                                             ▼
                                    Phase 6 (Presentation)
```

**Bottleneck:** `data_clean.csv` must be ready by Day 1 · 3:00 PM. Everything else is blocked until then. Member A should prioritise cleaning completeness over perfection — a 95% clean dataset delivered on time beats a perfect one delivered late.
