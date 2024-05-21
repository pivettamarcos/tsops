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

# MongoDB connection details
MONGO_HOST = "mongodb://adminuser:password123@127.0.0.1:33423"
MONGO_PORT = 33423
MONGO_DB = "tsops_dev_db"
MONGO_COLLECTION = "timeseries"

def load_data_mongo_to_csv(database_name, collection_name):
    warnings.filterwarnings("ignore")
    client = MongoClient(MONGO_HOST, MONGO_PORT)    
    db = client[database_name]
    collection = db[collection_name]

    tmpdir = tempfile.mkdtemp()

    data = list(collection.find())
    df = pd.DataFrame(data)


    filename = f'{database_name}_{collection_name}.csv'
    df.to_csv(os.path.join(tmpdir, filename), index=True)

    client.close()

    return tmpdir, filename

@click.command()
@click.option('--database_name', type=str, help='The name of the database')
@click.option('--collection_name', type=str, help='The name of the collection')

def load_raw_data(database_name, collection_name):
    tmpdir, filename = load_data_mongo_to_csv(database_name, collection_name)

    with mlflow.start_run(run_name="load_raw_data", nested=True) as mlrun:
        mlflow.log_artifact(os.path.join(tmpdir, filename), "raw_data")

        mlflow.set_tag("stage", "load_raw_data")
        mlflow.set_tag('dataset_uri', f'{mlrun.info.artifact_uri}/raw_data/{filename}')
        return
if __name__ == "__main__":
    print("\n=========== LOAD DATA =============")
    logging.info("\n=========== LOAD DATA =============")
    print("\nCurrent tracking uri: {}".format(mlflow.get_tracking_uri()))
    logging.info("\nCurrent tracking uri: {}".format(mlflow.get_tracking_uri()))
    load_raw_data()