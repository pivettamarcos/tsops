import os
import warnings
import sys
import click

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn import datasets, metrics

import mlflow
import mlflow.sklearn


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


@click.command()
@click.option("--alpha",
        type=float,
        default="0.1",
        help="Alpha parameter of the ElasticNet model.")
@click.option("--l1-ratio", 
        type=float,
        default="0.1",
        help="L1 ratio parameter of the ElasticNet model.")

def main(alpha, l1_ratio):
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    mlflow.set_experiment("wine-quality")

    # Enable auto-logging to MLflow
    mlflow.sklearn.autolog()

    # Load wine quality dataset
    X, y = datasets.load_wine(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(X_train, y_train)

        y_pred = lr.predict(X_test)
        metrics = eval_metrics(y_pred, y_test)

        print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
        print("  RMSE: %s" % rmse)
        print("  MAE: %s" % mae)
        print("  R2: %s" % r2)

        #mlflow.log_param("alpha", alpha)
        #mlflow.log_param("l1_ratio", l1_ratio)
        #mlflow.log_metric("rmse", rmse)
        #mlflow.log_metric("r2", r2)
        #mlflow.log_metric("mae", mae)
#
        #mlflow.sklearn.log_model(lr, "model")

def eval_metrics(pred, actual):
    rmse = np.sqrt(metrics.mean_squared_error(actual, pred))
    mae = metrics.mean_absolute_error(actual, pred)
    r2 = metrics.r2_score(actual, pred)
    return rmse, mae, r2

if __name__ == '__main__':
    main()