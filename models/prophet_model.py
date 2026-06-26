"""
CanAI Café — Prophet forecasting model.

Receives a prepared daily revenue Series and a TimeSeriesSplit object.
Implement the TODOs below before running notebooks/03_forecasting_model.ipynb §3.

Reference: docs/model_selection_rationale.md §5.1
"""

import numpy as np
import pandas as pd
import mlflow
import mlflow_setup
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

MODEL_NAME = "prophet"

# Hyperparameters — tune here, they are logged automatically on every run
PARAMS = {
    "yearly_seasonality": False,    # disabled: only 1 year of history, can't fit annual cycle reliably
    "weekly_seasonality": True,
    "daily_seasonality": False,
    "seasonality_mode": "multiplicative",
    "interval_width": 0.95,
    "n_changepoints": 15,           # reduced from default 25 to limit trend overfitting on 365-day series
}


def train(daily_revenue: pd.Series, train_idx) -> object:
    """
    Fit a Prophet model on the training slice.

    Parameters
    ----------
    daily_revenue : pd.Series
        Full daily revenue series indexed by date.
    train_idx : array-like
        Integer positions of the training window.

    Returns
    -------
    Fitted Prophet model.
    """
    from prophet import Prophet
    import logging
    logging.getLogger("prophet").setLevel(logging.WARNING)
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

    df = daily_revenue.iloc[train_idx].reset_index()
    df.columns = ["ds", "y"]
    m = Prophet(**PARAMS)
    m.add_country_holidays(country_name="CA")
    m.fit(df)
    return m


def evaluate(daily_revenue: pd.Series, tscv: TimeSeriesSplit) -> dict:
    """
    Run walk-forward cross-validation and log results to MLflow.

    Parameters
    ----------
    daily_revenue : pd.Series
        Full daily revenue series indexed by date.
    tscv : TimeSeriesSplit
        Shared splitter from the notebook (n_splits=5, test_size=30).

    Returns
    -------
    dict: fold_mae, fold_rmse, fold_mape, mean_mae, mean_rmse, mean_mape
    """
    mlflow_setup.setup()

    fold_mae, fold_rmse, fold_mape = [], [], []

    with mlflow.start_run(run_name=f"{MODEL_NAME}_cv"):
        mlflow.set_tag("model", MODEL_NAME)
        mlflow.set_tag("phase", "cross_validation")
        mlflow.set_tag("n_folds", tscv.n_splits)
        mlflow.log_params({**PARAMS, "country_holidays": "CA"})

        for fold, (train_idx, test_idx) in enumerate(tscv.split(daily_revenue)):
            m = train(daily_revenue, train_idx)

            n_test = len(test_idx)
            future = m.make_future_dataframe(periods=n_test)
            fc = m.predict(future)

            actuals = daily_revenue.iloc[test_idx].values
            preds = fc.tail(n_test)["yhat"].values

            mae  = mean_absolute_error(actuals, preds)
            rmse = np.sqrt(mean_squared_error(actuals, preds))
            mape = np.mean(np.abs((actuals - preds) / np.where(actuals != 0, actuals, np.nan))) * 100

            fold_mae.append(mae);  fold_rmse.append(rmse);  fold_mape.append(mape)
            mlflow.log_metric("fold_mae",  mae,  step=fold)
            mlflow.log_metric("fold_rmse", rmse, step=fold)
            mlflow.log_metric("fold_mape", mape, step=fold)

        mlflow.log_metrics({
            "mean_mae":  np.mean(fold_mae),
            "mean_rmse": np.mean(fold_rmse),
            "mean_mape": np.mean(fold_mape),
            "std_mape":  np.std(fold_mape),
        })

    return {
        "fold_mae":  fold_mae,
        "fold_rmse": fold_rmse,
        "fold_mape": fold_mape,
        "mean_mae":  np.mean(fold_mae),
        "mean_rmse": np.mean(fold_rmse),
        "mean_mape": np.mean(fold_mape),
    }


def forecast(daily_revenue: pd.Series, periods: int = 180) -> pd.DataFrame:
    """
    Refit on the full series and generate a forward forecast.

    Parameters
    ----------
    daily_revenue : pd.Series
        Full daily revenue series indexed by date.
    periods : int
        Number of days ahead to forecast (default 180 ≈ 6 months).

    Returns
    -------
    pd.DataFrame: month (YYYY-MM), forecasted_revenue, lower_bound, upper_bound
    """
    mlflow_setup.setup()

    with mlflow.start_run(run_name=f"{MODEL_NAME}_final_forecast"):
        mlflow.set_tag("model", MODEL_NAME)
        mlflow.set_tag("phase", "final_forecast")
        mlflow.log_params({**PARAMS, "forecast_periods": periods, "country_holidays": "CA"})

        all_idx = np.arange(len(daily_revenue))
        m = train(daily_revenue, all_idx)

        future = m.make_future_dataframe(periods=periods)
        fc = m.predict(future).tail(periods)[["ds", "yhat", "yhat_lower", "yhat_upper"]]

        fc["month"] = fc["ds"].dt.to_period("M").astype(str)
        monthly = fc.groupby("month")[["yhat", "yhat_lower", "yhat_upper"]].sum().reset_index()
        monthly.columns = ["month", "forecasted_revenue", "lower_bound", "upper_bound"]

        mlflow.log_metric("forecast_total_revenue", monthly["forecasted_revenue"].sum())
        mlflow.log_table(monthly, artifact_file="forecast_results.json")
        return monthly
