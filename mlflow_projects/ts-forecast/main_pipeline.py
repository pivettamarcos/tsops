import os
import warnings
import sys
import click

import pandas as pd
import numpy as np

import mlflow
import mlflow.sklearn
from mlflow.tracking.fluent import _get_experiment_id
from mlflow.utils import mlflow_tags
from mlflow.entities import RunStatus

import tempfile

from pymongo import MongoClient

#os.environ["MLFLOW_TRACKING_URI"] = "http://tsops-tracking-service:5001"
#mlflow.set_tracking_uri("http://tsops-tracking-service:5001")
MONGO_HOST = "mongodb://adminuser:password123@127.0.0.1:33423"
MONGO_PORT = 33423
MONGO_DB = "tsops_dev_db"
MONGO_COLLECTION = "timeseries"

mlflow.set_tracking_uri("http://127.0.0.1:43415")

def _already_ran(entry_point_name, parameters, git_commit, experiment_id=None):
    """Best-effort detection of if a run with the given entrypoint name,
    parameters, and experiment id already ran. The run must have completed
    successfully and have at least the parameters provided.
    """
    experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
    client = mlflow.tracking.MlflowClient()
    all_run_infos = reversed(client.search_runs(experiment_id))
    for run_info in all_run_infos:
        full_run = client.get_run(run_info.info.run_id)
        tags = full_run.data.tags
        if tags.get(mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT, None) != entry_point_name:
            continue
        match_failed = False
        for param_key, param_value in parameters.items():
            run_value = full_run.data.params.get(param_key)
            if run_value != param_value:
                match_failed = True
                break
        if match_failed:
            continue

        if run_info.info.status != "FINISHED":
            print(
                ("Run matched, but is not FINISHED, so skipping " "(run_id=%s, status=%s)")
                % (run_info.info.run_id, run_info.info.status)
            )
            continue

        previous_version = tags.get(mlflow_tags.MLFLOW_GIT_COMMIT, None)
        if git_commit != previous_version:
            print(
                (
                    "Run matched, but has a different source code version, so skipping "
                    "(found=%s, expected=%s)"
                )
                % (previous_version, git_commit)
            )
            continue
        return client.get_run(run_info.info.run_id)
    print("No matching run has been found.")
    return None

def _get_or_run(entrypoint, parameters, git_commit, ignore_previous_run=True, use_cache=True):
    if not ignore_previous_run:
        existing_run = _already_ran(entrypoint, parameters, git_commit)
        if use_cache and existing_run:
            print("Found existing run for entrypoint=%s and parameters=%s" % (entrypoint, parameters))
            return existing_run
    print("Launching new run for entrypoint=%s and parameters=%s" % (entrypoint, parameters))
    submitted_run = mlflow.run(uri=".", entry_point=entrypoint, run_name=entrypoint, parameters=parameters, env_manager="local")

    return mlflow.tracking.MlflowClient().get_run(submitted_run._run_id)

def load_raw_data(database_name, collection_name):
    client = MongoClient(MONGO_HOST, MONGO_PORT)    
    db = client[database_name]
    collection = db[collection_name]

    data = list(collection.find())
    df = pd.DataFrame(data)

    return df

@click.command()
@click.option('--darts_model', type=str, help='The Darts model to use')
@click.option('--database_name', type=str, help='The name of the database')
@click.option('--collection_name', type=str, help='The name of the collection')
@click.option('--ignore_previous_runs', type=bool, default=False, help='Ignore previous runs')

def main(darts_model, database_name, collection_name, ignore_previous_runs):
    warnings.filterwarnings("ignore")


    with mlflow.start_run(tags={"mlflow.runName": darts_model + '_pipeline'}) as active_run:
        mlflow.set_tag("stage", "main")
        git_commit = active_run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)

        # 1. Load Data
        load_raw_data_params = {"database_name": database_name,
                                "collection_name": collection_name}
        load_raw_data_run = _get_or_run("load_raw_data", load_raw_data_params, git_commit, ignore_previous_runs)  
        load_data_series_uri = load_raw_data_run.data.tags['dataset_uri']#.replace("s3:/", S3_ENDPOINT_URL)

        # 2. Train
        train_params = {"series_uri":load_data_series_uri,
                        "darts_model":darts_model}
        train_run = _get_or_run("train", train_params, git_commit, ignore_previous_runs)  

        return

if __name__ == '__main__':
    main()