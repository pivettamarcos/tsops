import logging
import mlflow
import pandas as pd
from pymongo import MongoClient
import tempfile
import click
import warnings
import os
from sklearn.linear_model import LinearRegression
import boto3

from utils import download_mlflow_artifact

from darts import TimeSeries
from darts.models import LinearRegressionModel
from darts.utils.model_selection import train_test_split
from darts.dataprocessing.transformers import MissingValuesFiller

import numpy as np



# MongoDB connection details
MONGO_HOST = "mongodb://adminuser:password123@127.0.0.1:33423"
MONGO_PORT = 33423
MONGO_DB = "tsops_dev_db"
MONGO_COLLECTION = "timeseries"

@click.command()
@click.option('--series_uri', type=str, help='The name of the database')
@click.option('--darts_model', type=str, help='The name of the collection')
def train(series_uri, darts_model):
    download_file_path = download_mlflow_artifact(series_uri)
    series_csv = download_file_path
    
    df = pd.read_csv(series_csv)

    ts = TimeSeries.from_dataframe(df, time_col="timestamp", value_cols=["melting","rainfall","flow"])

    filler = MissingValuesFiller()
    ts = filler.transform(ts)

    new_df_train, new_df_test = train_test_split(ts, test_size=0.2)

    train_target, test_target = new_df_train["flow"], new_df_test["flow"]
    train_future_cov, test_future_cov = new_df_train["rainfall"], new_df_test["rainfall"]
    train_past_cov, test_past_cov = new_df_train["melting"], new_df_test["melting"]

    input_chunk_length = 6
    output_chunk_length = 6

    hyperparams={'lags': input_chunk_length,
            'lags_past_covariates': input_chunk_length,
            'lags_future_covariates': (input_chunk_length, output_chunk_length) }
    
    model = LinearRegressionModel(**hyperparams)

    model.fit(
        series=train_target, 
        past_covariates=train_past_cov,
        future_covariates=train_future_cov,
    )

    historical_forecasts = model.historical_forecasts(
        train_target.append(test_target),
        past_covariates= train_past_cov.append(test_past_cov),
        future_covariates=train_future_cov.append(test_future_cov),
        start=len(train_target),
        forecast_horizon=output_chunk_length,
        retrain=False,
        last_points_only=False,
    )

    print(historical_forecasts)

if __name__ == "__main__":
    print("\n=========== TRAIN =============")
    logging.info("\n=========== TRAIN =============")
    print("\nCurrent tracking uri: {}".format(mlflow.get_tracking_uri()))
    logging.info("\nCurrent tracking uri: {}".format(mlflow.get_tracking_uri()))
    train()