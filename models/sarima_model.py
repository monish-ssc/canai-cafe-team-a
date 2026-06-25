"""
CanAI Cafe - SARIMA forecasting model.

Receives a prepared daily revenue Series and a TimeSeriesSplit object.
Uses SARIMA(1,0,1)(1,1,0)[7] as the default configuration.

Reference: docs/model_selection_rationale.md S5.2
"""

import numpy as np
import pandas as pd
import mlflow
import mlflow_setup
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

MODEL_NAME = "sarima"

# Hyperparameters — tune here, they are logged automatically on every run
PARAMS = {
    "order": (1, 0, 1),          # (p, d, q)
    "seasonal_order": (1, 1, 0, 7),  # (P, D, Q, period)
    "enforce_stationarity": True,
    "enforce_invertibility": True,
}


def train(daily_revenue: pd.Series, train_idx) -> object:
    """
    Fit a SARIMA model on the training slice.

    Parameters
    ----------
    daily_revenue : pd.Series
        Full daily revenue series indexed by date.
    train_idx : array-like
        Integer positions of the training window. Must be a contiguous
        slice — SARIMAX requires an ordered time series, not shuffled rows.

    Returns
    -------
    Fitted SARIMAXResults object.
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    series = daily_revenue.iloc[train_idx]
    series = series.asfreq("D")
    model = SARIMAX(series, order=PARAMS["order"], seasonal_order=PARAMS["seasonal_order"],
                    enforce_stationarity=PARAMS["enforce_stationarity"],
                    enforce_invertibility=PARAMS["enforce_invertibility"])
    return model.fit(disp=False)


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
        mlflow.log_params({
            "order_p": PARAMS["order"][0],
            "order_d": PARAMS["order"][1],
            "order_q": PARAMS["order"][2],
            "seasonal_P": PARAMS["seasonal_order"][0],
            "seasonal_D": PARAMS["seasonal_order"][1],
            "seasonal_Q": PARAMS["seasonal_order"][2],
            "seasonal_period": PARAMS["seasonal_order"][3],
        })

        for fold, (train_idx, test_idx) in enumerate(tscv.split(daily_revenue)):
            result  = train(daily_revenue, train_idx)
            fc      = result.get_forecast(steps=len(test_idx))
            preds   = fc.predicted_mean.values
            actuals = daily_revenue.iloc[test_idx].values

            mae  = mean_absolute_error(actuals, preds)
            rmse = np.sqrt(mean_squared_error(actuals, preds))
            mape = np.mean(np.abs((actuals - preds) / actuals)) * 100

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
        mlflow.log_params({
            "order_p": PARAMS["order"][0], "order_d": PARAMS["order"][1], "order_q": PARAMS["order"][2],
            "seasonal_P": PARAMS["seasonal_order"][0], "seasonal_D": PARAMS["seasonal_order"][1],
            "seasonal_Q": PARAMS["seasonal_order"][2], "seasonal_period": PARAMS["seasonal_order"][3],
            "forecast_periods": periods,
        })

        from statsmodels.tsa.statespace.sarimax import SARIMAX
        series = daily_revenue.asfreq("D")
        model = SARIMAX(series, order=PARAMS["order"],
                        seasonal_order=PARAMS["seasonal_order"],
                        enforce_stationarity=PARAMS["enforce_stationarity"],
                        enforce_invertibility=PARAMS["enforce_invertibility"])
        result = model.fit(disp=False)
        fc = result.get_forecast(steps=periods)
        pred_df = pd.DataFrame({
            "date":  pd.date_range(daily_revenue.index[-1] + pd.Timedelta(days=1), periods=periods),
            "yhat":  fc.predicted_mean.values,
            "lower": fc.conf_int(alpha=0.05).iloc[:, 0].values,
            "upper": fc.conf_int(alpha=0.05).iloc[:, 1].values,
        })
        pred_df["month"] = pred_df["date"].dt.to_period("M").astype(str)
        monthly = pred_df.groupby("month")[["yhat", "lower", "upper"]].sum().reset_index()
        monthly.columns = ["month", "forecasted_revenue", "lower_bound", "upper_bound"]

        mlflow.log_metric("forecast_total_revenue", monthly["forecasted_revenue"].sum())
        mlflow.log_table(monthly, artifact_file="forecast_results.json")
        return monthly
