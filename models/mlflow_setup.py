"""
CanAI Café — MLflow tracking configuration.

All three model modules import this to ensure they log to the same
experiment and backend store, regardless of where they are called from
(notebook, script, or interactive session).

Tracking data is stored under mlruns/ at the project root and committed
to git so the full experiment history travels with the repository.

Usage
-----
    import mlflow_setup
    mlflow_setup.setup()          # call once before any mlflow.start_run()

Viewing results
---------------
From the project root:
    mlflow ui --backend-store-uri ./mlruns --port 5000
Then open http://localhost:5000
"""

import os
import mlflow

_MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MODELS_DIR)

TRACKING_URI = f"file:///{os.path.join(_PROJECT_ROOT, 'mlruns').replace(os.sep, '/')}"
EXPERIMENT_NAME = "canai-cafe-forecasting"


def setup() -> None:
    """Set the tracking URI and activate the shared experiment."""
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)


def active_run_url() -> str:
    """Return a hint for locating the last active run in the UI."""
    run = mlflow.active_run()
    if run is None:
        return "(no active run)"
    return f"http://localhost:5000/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}"
