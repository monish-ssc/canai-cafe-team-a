# Data Cleaning Summary

**Dataset:** CanAI Café Transactions (`data/raw/Team A CanAI Cafe dataset.xlsx`)
**Cleaned by:** Member A
**Date:** *(fill in when notebook is run)*
**Notebook:** `notebooks/01_data_cleaning.ipynb`
**Audit log:** `data/clean/cleaning_audit_log.csv`

---

## Before Cleaning

| Metric | Value |
|--------|-------|
| Total rows | 10,000 |
| Total columns | 9 |
| Columns with nulls | 6 — Item, Quantity, Payment Method, Location, Transaction Date, Province |
| Fully duplicate rows | 0 |
| Duplicate Transaction IDs | 84 rows across colliding IDs (different transactions, not duplicates) |

---

## Issues Found & Actions Taken

| Step | Column | Issue | Action Taken | Rows Affected |
|------|--------|-------|--------------|---------------|
| 4a | All columns | Empty / whitespace-only string cells | Replaced with `NaN` | ~358 cells |
| 4b | Item | 87 null + 13 whitespace-only values | Row dropped | 100 |
| 4c | Quantity | 78 null values (after Item drop) | Row dropped | 78 |
| 4d | Transaction Date | 172 null values (after Quantity drop) | Row dropped | 172 |
| 4e | Payment Method | 419 null values (after prior drops) | Filled with `'Unknown'` | 419 |
| 4f | Location | 690 null values | Filled with `'Unknown'` | 690 |
| 4g | Province | 336 null values | Filled with `'Unknown'` | 336 |
| 5a | All columns | Fully duplicate rows | Dropped | 0 (none found) |
| 5b | Transaction ID | 84 rows share a non-unique Transaction ID | Rows retained; `Row_ID` surrogate key added | 0 removed |
| 6a | Payment Method | `ERR_PM_102` error code | Replaced with `'Unknown'` | 26 |
| 7a | Item | Typos / case variants (cofee, C0ffee, Tee, Donutt, Sandwhich …) | Mapped to canonical name | 1,243 |
| 7b | Province | Abbreviations / typos / case variants (BC, NL, SK, MB, Saskatchewn …) | Mapped to full official province name | 3,421 |
| 7c | Transaction Date | Stored as string/object dtype; 63 unparseable strings | Parsed to `datetime64`; unparseable rows dropped | 9,663 parsed / 63 dropped |
| 7d | Quantity | Non-numeric values coerced to NaN | Row dropped | 20 |
| 7e | Quantity | Stored as object dtype | Cast to `int64` | all rows |
| 8a | Total Spent | Validated against `Quantity × Price Per Unit` | No action required (all matched) | 0 |
| 8b | Transaction Date | Dates outside 2023 | No action required (all within 2023) | 0 |
| 8c | Quantity | Values outside expected range 1–5 | No action required (all in range) | 0 |

> **Note on dropped-row counts:** Because rows can be null in multiple columns simultaneously, drops in steps 3b–3d do not add up — each step only removes rows that survive the previous step. See `cleaning_audit_log.csv` for exact sequential counts.

### Item canonical name mapping

| Canonical | Dirty variants normalised |
|-----------|--------------------------|
| Coffee | `coffee`, `cofee`, `coffe`, `Cofee`, `C0ffee` |
| Tea | `Tee`, `tee`, `TEA` |
| Donut | `donut`, `Donutt`, `Doughnut` |
| Juice | `juice`, `Juic`, `Juicee` |
| Sandwich | `sandwich`, `Sandwhich` |

### Province canonical name mapping

| Canonical | Dirty variants normalised |
|-----------|--------------------------|
| British Columbia | `british columbia`, `BritishColumbia`, `B.C.`, `BC`, `BRITISH COLUMBIA`, `British Columba`, `British Columbi` |
| Newfoundland and Labrador | `Newfoundland`, `New Foundland`, `NFLD`, `NL`, `newfoundland and labrador`, `NEWFOUNDLAND`, `newfoundland`, `Newfoundlan` |
| Saskatchewan | `Saskatchewn`, `Sask.`, `SK`, `SASKATCHEWAN`, `Sasktchewan`, `Saskatchewa`, `saskatchewan` |
| Manitoba | `Manitba`, `MB`, `MANITOBA`, `Manitobaa`, `Manitob`, `mb`, `manitoba` |
| Ontario | `Ont.`, `ON`, `ontario`, `Ontaroi`, `Ontairo` — ⚠ flagged (see caveats) |

---

## After Cleaning

| Metric | Value |
|--------|-------|
| Total rows | 9,567 |
| Total columns | 10 (original 9 + `Row_ID`) |
| Remaining nulls | None (nulls either dropped or filled with `'Unknown'`) |
| Rows removed | 433 |
| % of rows retained | 95.7% |

> **Note:** Re-run `01_data_cleaning.ipynb` top-to-bottom after the whitespace fix to regenerate `data_clean.csv` and `cleaning_audit_log.csv` with these exact counts.

---

## Known Caveats & Limitations

- **Ontario rows:** A small number of transactions show `Province = 'Ontario'`, which is outside the expected 4-province scope (BC, MB, SK, NL). These are retained with a warning — verify with the data source before including in provincial analysis.
- **Duplicate Transaction IDs:** 84 rows share a non-unique Transaction ID with different items and dates, indicating an ID-generation collision in the source system (not duplicate orders). A surrogate `Row_ID` column was added for downstream joins and Power BI relationships.
- **`'Unknown'` values:** ~5–9% of rows have unknown payment method or location after filling. Analyses that filter or group on these fields will undercount due to the `'Unknown'` group — note this in any visuals.
- **`Total Spent` is a derived column:** It equals `Quantity × Price Per Unit` exactly for all valid rows. It was not recalculated — only validated.
- **Dropped rows note:** Rows dropped in steps 3b–3d are removed sequentially, so a row missing both Item and Quantity is only counted once (under 3b). Total rows removed is less than the sum of individual column null counts.
- **Full audit log:** Step-by-step change record with exact row counts is at `data/clean/cleaning_audit_log.csv`.
