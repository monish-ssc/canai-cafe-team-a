# Forecasting Model Selection Rationale

**Dataset:** CanAI Café Transactions (`data/clean/data_clean.csv`)  
**Task:** 6-month revenue forecast with confidence intervals  
**Prepared by:** Member C  
**Date:** 2026-06-25  
**Notebook:** `notebooks/03_forecasting_model.ipynb`

---

## 1. Problem Framing

The forecasting target is **total daily revenue** aggregated from individual café transactions. The goal is to produce a **monthly 6-month forward forecast** (July – December 2024) with lower and upper confidence bounds, exported as `forecast_results.csv`.

**Inputs available:**
- Transaction Date (daily grain, Jan 1 – Dec 31 2023)
- Total Spent per transaction (target when summed daily)
- Item, Province, Location, Payment Method (categorical covariates)

---

## 2. Time Series Diagnostics

All statistics below were computed from the daily aggregated revenue series (`data_clean.csv` → group by `Transaction Date` → sum `Total Spent`).

### 2.1 Dataset Overview

| Property | Value |
|----------|-------|
| Records | 9,483 transactions |
| Date range | 2023-01-01 to 2023-12-31 |
| Unique dates | 365 (no gaps — every calendar day has at least one transaction) |
| History length | 1 year |
| Daily revenue mean | $224.50 |
| Daily revenue std | $100.20 |
| Daily CV | 0.446 (high daily variance) |
| Monthly CV | 0.060 (very stable monthly totals) |

### 2.2 Stationarity (Augmented Dickey-Fuller Test)

| Metric | Value |
|--------|-------|
| ADF Statistic | −4.589 |
| p-value | 0.000136 |
| Conclusion | **Stationary** (reject unit-root null at p < 0.001) |

The series requires **no differencing**. Level-based models can be applied directly.

### 2.3 Seasonal Decomposition

| Decomposition Period | Seasonal Amplitude |
|----------------------|--------------------|
| Weekly (period = 7) | **197.4** |
| Monthly (period = 30) | 48.1 |
| Trend range | $181.4 – $290.1 (gradual upward drift) |

**Finding:** Weekly seasonality is the dominant pattern, with an amplitude of $197 — nearly the full daily mean. Monthly/annual seasonality is negligible in comparison (amplitude $48).

### 2.4 Autocorrelation Function (ACF)

| Lag | ACF Value | Interpretation |
|-----|-----------|----------------|
| 1 | 0.202 | Mild positive autocorrelation |
| 2 | −0.295 | Negative (mid-week correction) |
| 3 | −0.264 | Negative |
| 7 | **0.729** | Very strong — same day last week |
| 14 | **0.692** | Strong — two weeks ago |

**Finding:** The lag-7 ACF of 0.73 is definitive evidence of a strong weekly seasonal cycle. Any chosen model must explicitly handle period-7 seasonality.

### 2.5 Monthly Revenue Totals

| Month | Revenue ($) |
|-------|-------------|
| Jan | 6,911.50 |
| Feb | 6,403.50 |
| Mar | 6,911.50 |
| Apr | 6,684.00 |
| May | 7,420.50 |
| Jun | 7,470.00 |
| Jul | 6,268.00 |
| Aug | 7,406.50 |
| Sep | 6,435.00 |
| Oct | 6,747.50 |
| Nov | 6,600.50 |
| Dec | 6,674.00 |

Monthly totals are very stable (CV = 0.06), confirming no strong annual cycle. The variance is almost entirely explained by the day-of-week effect.

---

## 3. Data Constraints Relevant to Modeling

| Constraint | Implication |
|------------|-------------|
| **1 year of history** | Annual seasonality cannot be reliably estimated — only 1 cycle observed |
| **Strong weekly pattern (lag-7 ACF = 0.73)** | Model must encode weekly period explicitly |
| **No missing dates** | No imputation needed before fitting |
| **Stationary series** | No log transform or differencing required |
| **Forecast horizon = 6 months (~180 days)** | Long horizon relative to 1-year history — uncertainty intervals will be wide |
| **Categorical covariates available** | Feature-based models (XGBoost) can exploit Item, Province, Location |

---

## 4. Candidate Models Evaluated

Six model families were considered. The table below summarises the evaluation.

| # | Model | Weekly Seasonality | Annual Seasonality | Handles Covariates | Confidence Intervals | Data Requirement | Verdict |
|---|-------|-------------------|-------------------|-------------------|---------------------|-----------------|---------|
| 1 | **Prophet** | Native (Fourier) | Native (but weak here) | Yes (regressors) | Yes (probabilistic) | Low — 1 year sufficient | Selected |
| 2 | **SARIMA(p,d,q)(P,D,Q)[7]** | Explicit (period=7) | No | No | Yes (parametric) | Medium | Selected |
| 3 | **XGBoost + lag features** | Via lag-7 features | Via month indicator | Yes (native) | Approximated (quantile) | Low–Medium | Selected |
| 4 | Holt-Winters (ETS) | Yes (multiplicative) | Limited | No | Yes | Low | Not selected — covered by Prophet |
| 5 | LSTM / RNN | Via memory | Via memory | Yes | No (unless MC) | High — needs 3–5 years | Not selected — insufficient data |
| 6 | Linear Regression baseline | Via dummies | Via dummies | Yes | Yes | Very low | Not selected — benchmark only |

---

## 5. Recommended Models (Top 3)

### 5.1 Model 1 — Prophet (Primary Recommendation)

**Library:** `prophet` (already in `requirements.txt`)  
**Type:** Additive decomposition — trend + seasonality + holidays + noise

**Why it fits this data:**

Prophet decomposes the time series into an additive model:

```
y(t) = trend(t) + seasonality(t) + holidays(t) + noise(t)
```

- **Weekly seasonality** is handled via Fourier series (default `weekly_seasonality=True`). With lag-7 ACF = 0.73, this component will dominate the fit.
- **Trend** is modelled with a piecewise linear or logistic growth function, which captures the observed drift from $181 to $290 over the year.
- **Annual seasonality** is included but will have high uncertainty because only 1 year of data exists — Prophet's Bayesian priors help regularise this.
- **Uncertainty intervals** are generated via a Monte Carlo posterior simulation, producing the `lower_bound` / `upper_bound` columns needed in `forecast_results.csv`.
- **Robustness**: Prophet is designed for business time series with irregular patterns, outliers, and short histories — exactly this use case.
- **Already a dependency**: Zero additional installation cost.

**Key configuration:**

```python
from prophet import Prophet

m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,   # no sub-daily data
    seasonality_mode='additive',
    interval_width=0.95
)
m.fit(df_prophet)  # columns: ds, y
future = m.make_future_dataframe(periods=180)
forecast = m.predict(future)
```

**Limitations:**
- Annual seasonality estimate is unreliable with only 1 year of history — wide CIs expected.
- No native multi-step exogenous regressor support (would need manual regressor forecasts).
- Black-box trend changepoints may over-fit on a short series if `n_changepoints` is not tuned.

**Mitigation:** Disable `yearly_seasonality` or use `seasonality_prior_scale=0.1` to down-weight it.

---

### 5.2 Model 2 — SARIMA(p,d,q)(P,D,Q)[7]

**Library:** `statsmodels.tsa.statespace.SARIMAX`  
**Type:** Classical parametric time series model

**Why it fits this data:**

SARIMA is purpose-built for stationary time series with explicit seasonal periods. The diagnostic evidence makes it a strong fit:

- **d = 0** (series is stationary — ADF p = 0.00014, no differencing needed)
- **Seasonal period = 7** (weekly cycle confirmed by ACF lag-7 = 0.73, lag-14 = 0.69)
- **D = 1** (one seasonal difference at period 7 to handle the strong weekly cycle)
- Starting AR/MA order: SARIMA(1,0,1)(1,1,0)[7] as an initial candidate, refined via AIC grid search

The negative ACF at lags 2–3 suggests an MA component captures the within-week inversion after the weekend peak. The strong seasonal ACF suggests a seasonal AR(1) term.

**Candidate parameter grid (evaluated by AIC):**

| p | d | q | P | D | Q | Period |
|---|---|---|---|---|---|--------|
| 1 | 0 | 1 | 1 | 1 | 0 | 7 |
| 2 | 0 | 1 | 1 | 1 | 1 | 7 |
| 1 | 0 | 2 | 0 | 1 | 1 | 7 |

**Key configuration:**

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

model = SARIMAX(
    daily_revenue,
    order=(1, 0, 1),
    seasonal_order=(1, 1, 0, 7),
    enforce_stationarity=True,
    enforce_invertibility=True
)
result = model.fit(disp=False)
forecast = result.get_forecast(steps=180)
conf_int = forecast.conf_int(alpha=0.05)
```

**Limitations:**
- Assumes linear relationships and Gaussian errors — may underfit high-variance days.
- 6-month horizon (180 steps ahead) from only 365 training points means confidence intervals will widen significantly at the tail.
- Does not natively use the categorical covariates (Item, Province, etc.) without extension to SARIMAX.
- Grid search over (p, d, q)(P, D, Q) is computationally expensive — use `pmdarima.auto_arima` or a narrow grid.

**Mitigation:** Use `auto_arima` from `pmdarima` with `seasonal=True, m=7` for automatic order selection.

---

### 5.3 Model 3 — XGBoost Regressor with Lag Features

**Library:** `scikit-learn` (pipeline) + `xgboost` (already in `requirements.txt` via scikit-learn ecosystem)  
**Type:** Gradient-boosted trees with engineered time features

**Why it fits this data:**

XGBoost is not a native time series model but becomes one through feature engineering. It is included because:

1. **Rich covariates**: Item type, Province, Location, and Payment Method are available per transaction. These categorical dimensions can reveal which product categories or regions drive revenue on specific days — information that Prophet and SARIMA cannot use.

2. **Non-linear interactions**: XGBoost captures non-linear effects (e.g., "Coffee sales spike in BC on weekends") that additive decomposition models miss.

3. **lag-7 feature is highly informative**: ACF lag-7 = 0.73 means `revenue_lag_7` is a near-perfect predictor, giving XGBoost a strong signal to learn from.

**Feature engineering plan:**

| Feature | Rationale |
|---------|-----------|
| `lag_7`, `lag_14` | Direct weekly cycle signal (ACF evidence) |
| `rolling_mean_7`, `rolling_mean_14` | Smoothed trend signal |
| `day_of_week` (0–6) | Captures within-week pattern |
| `month` (1–12) | Captures any slow annual drift |
| `week_of_year` | Finer annual resolution |
| `is_holiday` (Canadian holidays) | Anomaly correction |
| `item_revenue_share_*` | Daily item-mix signals per aggregated day |

**Key configuration:**

```python
import xgboost as xgb
from sklearn.pipeline import Pipeline

# Feature matrix built from daily revenue + lag/calendar features
# Split via TimeSeriesSplit — see Section 6
X_train, X_val = ...
y_train, y_val = ...

model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
```

**Forecasting approach (recursive / direct):**
Because XGBoost is not auto-regressive, the 6-month forecast is generated using the **recursive strategy**: predict day t+1 using real lags, then append the prediction to the series and repeat for t+2, t+3 … t+180. Uncertainty is approximated using **quantile regression** (`objective='reg:quantileerror'`) at the 5th and 95th percentile.

**Limitations:**
- Recursive forecasting compounds prediction errors over the 180-day horizon — uncertainty will be underestimated at the tail.
- Overfitting risk is higher with only 365 training rows and many features — requires careful regularisation (`max_depth=3–4`, `subsample=0.8`).
- Does not extrapolate trends beyond the training range; if the trend continues upward, XGBoost will underestimate future revenue.
- Feature engineering requires additional time to implement correctly.

**Mitigation:** Use `TimeSeriesSplit` cross-validation (see Section 6) to evaluate across all seasons; tune with `early_stopping_rounds`.

---

## 6. Evaluation Framework

### 6.1 Why not shuffle the train/test split

A random shuffle split is not valid for time series data, for two reasons:

**Data leakage.** This model's most informative features are `lag_7` and `lag_14` — the revenue values from 7 and 14 days prior. If the dataset is shuffled, a test row from January could be "predicted" using a lag-7 value that was assigned to the training set. The model has already seen that value, so the evaluation is measuring interpolation of known history rather than prediction of an unseen future. SARIMA cannot be shuffled at all — it requires a contiguous time series as input by mathematical definition.

**Wrong simulation of the real-world task.** The actual forecast we need to produce is July–December 2024, trained on all of 2023. Any evaluation method should approximate this scenario: train on earlier data, evaluate on later data.

**The concern that motivates shuffling is valid, however.** A single Jan–Oct train / Nov–Dec test window evaluates the model only against winter months and never exposes it to spring or summer patterns during training. That seasonal skew is real.

### 6.2 Correct approach: walk-forward (time-series) cross-validation

The solution is **TimeSeriesSplit** from scikit-learn, which creates multiple ordered train/test folds that advance through the year. Each fold trains on everything before a cutoff and tests on the next window after it — preserving temporal order and eliminating leakage while ensuring every month of the year appears as a test period in some fold.

**Configuration for this dataset (365 days, 5 folds, ~30-day test windows):**

```
Fold 1: Train Jan–Jul  (≈210 days) │ Test Aug       (30 days)
Fold 2: Train Jan–Aug  (≈240 days) │ Test Sep       (30 days)
Fold 3: Train Jan–Sep  (≈270 days) │ Test Oct       (30 days)
Fold 4: Train Jan–Oct  (≈300 days) │ Test Nov       (30 days)
Fold 5: Train Jan–Nov  (≈330 days) │ Test Dec       (30 days)
```

This tests the model against summer (Aug), autumn (Sep–Oct), and winter (Nov–Dec), giving a seasonally balanced view of generalisation quality.

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
import numpy as np

tscv = TimeSeriesSplit(n_splits=5, test_size=30)

fold_maes = []
for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    fold_maes.append(mean_absolute_error(y_test, preds))

print(f"Mean MAE across folds: {np.mean(fold_maes):.2f}")
print(f"Fold MAEs: {[round(m, 2) for m in fold_maes]}")
```

**For Prophet and SARIMA**, which require a contiguous series, cross-validation is implemented by re-fitting the model on the training slice of each fold and then forecasting the test window directly — not by selecting rows.

### 6.3 Consistent split across all three models

The same 5-fold `TimeSeriesSplit` is applied to all three models. A different split strategy per model was considered but rejected: if the test windows differ, any difference in MAPE could be explained by the data each model happened to be tested on rather than by the model itself. Keeping the split identical isolates the model as the only variable and makes the per-fold MAEs directly comparable.

What does vary per model is the *mechanics* of applying the split, not the data:

- **Prophet / SARIMA** — each fold's training slice is passed as a contiguous time series; the model forecasts the test window directly.
- **XGBoost** — the same date range is used, but the training slice is presented as a feature matrix (lag values, calendar features, etc.).

Using different split strategies per model would be appropriate if the goal were hyperparameter tuning for a single model (e.g., testing whether SARIMA performs better with a longer warm-up window). That is a separate question from "which of these three models generalises best to this data."

### 6.5 Final training for forecast

Once cross-validation confirms acceptable performance, **all 365 days of 2023 data are used to train the final model** before generating the 6-month forward forecast. No data is held back at inference time — the full history improves parameter estimates for the real forecast.

### 6.6 Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| MAE | mean(|y − ŷ|) | Average absolute error in dollars |
| RMSE | sqrt(mean((y − ŷ)²)) | Penalises large errors more heavily |
| MAPE | mean(|y − ŷ| / y) × 100 | Percentage error — scale-independent |

Metrics are reported **per fold** and as a **mean ± std across folds** to surface any months where the model degrades.

**Acceptance threshold:** Mean MAPE < 20% across all folds is considered acceptable for a 1-year-history café forecast.

---

## 7. Model Selection Decision Matrix

| Criterion | Weight | Prophet | SARIMA | XGBoost |
|-----------|--------|---------|--------|---------|
| Handles weekly seasonality | High | Yes — native Fourier terms | Yes — explicit period=7 | Yes — via lag-7 feature |
| Confidence intervals | High | Yes — posterior simulation | Yes — parametric | Approximate — quantile regression only |
| Short history (1 year) | High | Yes — designed for short series | Marginal — seasonal ARIMA needs sufficient cycles | Yes — tree models generalise with less data |
| Interpretability | Medium | Yes — decomposable trend/seasonality components | Yes — explicit AR/MA coefficients | Limited — feature importance only |
| Uses categorical covariates | Medium | Partial — manual regressors required | No | Yes — native support |
| Already in dependencies | Low | Yes | No — requires statsmodels | No — requires xgboost |
| Implementation complexity | Low | Low | Medium | High |

**Primary model for final forecast: Prophet** — lowest implementation complexity, native uncertainty intervals, directly installed, handles the dominant weekly pattern, and is robust to the short-history limitation.

**Fallback / comparison: SARIMA** — classical and interpretable; provides a statistical benchmark. If Prophet MAPE is unacceptable, SARIMA is the next candidate.

**Exploratory: XGBoost** — run if time permits; most likely to capture item/region interactions but highest engineering cost and uncertainty in long-horizon recursive forecasting.

---

## 8. Output Specification

The final model will produce `outputs/forecast_results.csv` with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `month` | string | Format `YYYY-MM` (e.g., `2024-01`) |
| `forecasted_revenue` | float | Monthly total predicted revenue |
| `lower_bound` | float | 95% confidence interval lower bound |
| `upper_bound` | float | 95% confidence interval upper bound |

Daily forecasts are aggregated to monthly totals before export.

---

## 9. References

- Taylor, S.J. & Letham, B. (2018). *Forecasting at Scale*. The American Statistician, 72(1), 37–45.  
- Box, G.E.P., Jenkins, G.M., Reinsel, G.C., & Ljung, G.M. (2015). *Time Series Analysis: Forecasting and Control* (5th ed.). Wiley.  
- Chen, T. & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. KDD '16 Proceedings.
