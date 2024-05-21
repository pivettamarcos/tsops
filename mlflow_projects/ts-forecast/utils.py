import os
import mlflow

def download_mlflow_artifact(url, dst_dir=None):
    import sys
    import tempfile
    import requests
    filepath = mlflow.artifacts.download_artifacts(url)
    if dst_dir is None:
        dst_dir = tempfile.mkdtemp()
    else:
        os.makedirs(dst_dir, exist_ok=True)

    return filepath