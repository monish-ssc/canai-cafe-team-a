"""
CanAI Café — XGBoost forecasting model.

Receives a prepared daily revenue Series and a TimeSeriesSplit object.
Implement the TODOs below before running notebooks/03_forecasting_model.ipynb §5.

Feature engineering plan (see docs/model_selection_rationale.md §5.3):
    lag_7, lag_14               — weekly cycle signal (ACF lag-7 = 0.73)
    rolling_mean_7/14           — smoothed trend
    day_of_week (0–6)           — within-week pattern
    month (1–12)                — slow annual drift
    week_of_year                — finer annual resolution
    is_holiday                  — Canadian statutory holidays

Reference: docs/model_selection_rationale.md §5.3
"""

import numpy as np
import pandas as pd
import mlflow
import mlflow_setup
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

MODEL_NAME = "xgboost"

# Hyperparameters — tune here, they are logged automatically on every run
PARAMS = {
    "n_estimators": 300,
    "max_depth": 4,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
}


def build_features(daily_revenue: pd.Series) -> pd.DataFrame:
    """
    Engineer the feature matrix from the daily revenue series.

    Parameters
    ----------
    daily_revenue : pd.Series
        Daily revenue indexed by date.

    Returns
    -------
    pd.DataFrame
        Feature matrix aligned to daily_revenue's index.
        Rows with NaN lag values (first 14 days) are dropped.
    """
    # TODO: implement
    # df = daily_revenue.rename("revenue").to_frame()
    # df["lag_7"]           = df["revenue"].shift(7)
    # df["lag_14"]          = df["revenue"].shift(14)
    # df["rolling_mean_7"]  = df["revenue"].shift(1).rolling(7).mean()
    # df["rolling_mean_14"] = df["revenue"].shift(1).rolling(14).mean()
    # df["day_of_week"]     = df.index.dayofweek
    # df["month"]           = df.index.month
    # df["week_of_year"]    = df.index.isocalendar().week.astype(int)
    # df = df.dropna()
    # return df
    raise NotImplementedError


def train(daily_revenue: pd.Series, train_idx) -> object:
    """
    Build features and fit an XGBoost regressor on the training slice.

    Parameters
    ----------
    daily_revenue : pd.Series
        Full daily revenue series indexed by date.
    train_idx : array-like
        Integer positions of the training window.

    Returns
    -------
    Fitted XGBRegressor.
    """
    # TODO: implement
    # import xgboost as xgb
    # features = build_features(daily_revenue)
    # train_features = features.iloc[train_idx]
    # X_train = train_features.drop(columns="revenue")
    # y_train = train_features["revenue"]
    # model = xgb.XGBRegressor(**PARAMS)
    # model.fit(X_train, y_train)
    # return model
    raise NotImplementedError


def evaluate(daily_revenue: pd.Series, tscv: TimeSeriesSplit) -> dict:
    """
    Run walk-forward cross-validation and log results to MLflow.

    Uses the recursive forecasting strategy for the test window:
    predict t+1 → append to series → predict t+2 → … → t+30.

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
        mlflow.log_params(PARAMS)

        for fold, (train_idx, test_idx) in enumerate(tscv.split(daily_revenue)):
            # TODO: train on slice, recursively predict test window
            raise NotImplementedError

            # model   = train(daily_revenue, train_idx)
            # actuals = daily_revenue.iloc[test_idx].values
            # preds   = []  # recursive predictions go here
            #
            # mae  = mean_absolute_error(actuals, preds)
            # rmse = np.sqrt(mean_squared_error(actuals, preds))
            # mape = np.mean(np.abs((actuals - preds) / actuals)) * 100
            #
            # fold_mae.append(mae);  fold_rmse.append(rmse);  fold_mape.append(mape)
            # mlflow.log_metric("fold_mae",  mae,  step=fold)
            # mlflow.log_metric("fold_rmse", rmse, step=fold)
            # mlflow.log_metric("fold_mape", mape, step=fold)

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
    Refit on the full series and generate a forward forecast using the
    recursive strategy. Uncertainty bounds use quantile regression
    (5th and 95th percentile models).

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
        mlflow.log_params({**PARAMS, "forecast_periods": periods})

        # TODO: fit on full series, recursive forecast, aggregate to monthly
        raise NotImplementedError

        # import xgboost as xgb
        # model_median = train(daily_revenue, range(len(daily_revenue)))
        # model_lower  = xgb.XGBRegressor(**{**PARAMS, "objective": "reg:quantileerror", "quantile_alpha": 0.05})
        # model_upper  = xgb.XGBRegressor(**{**PARAMS, "objective": "reg:quantileerror", "quantile_alpha": 0.95})
        # # fit lower/upper on full feature matrix, then recursive predict ...
        #
        # mlflow.log_metric("forecast_total_revenue", monthly["forecasted_revenue"].sum())
        # mlflow.log_table(monthly, artifact_file="forecast_results.json")
        # return monthly
