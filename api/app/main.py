from typing import Union

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
import pymongo

from pymongo import MongoClient
from io import BytesIO
import json
from bson import json_util

from typing import Literal, List

from datetime import datetime, timedelta

import friendlywords as fw

import pandas as pd

#ROOT_PATH = '/'

description = ""

tags_metadata = [
    {
        "name": "forecast",
        "description": "Infer future points using forecasting models",
    },
]

app = FastAPI(  
    #root_path=ROOT_PATH,
    title="tsops-api",
    description=description,
    version="0.0.1",
    contact={
        "name": "Marcos Pivetta",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/license/mit/",
    },
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_MAX_AGE = int(timedelta(days=365).total_seconds())

@app.get("/health", tags=["system"])
def health():
    return {"is_healthy": True}


@app.get("/version", tags=["system"])
def health():
    return {"version": "0.0.1"}


# MongoDB connection details
MONGO_HOST = "mongodb://adminuser:password123@127.0.0.1:33423"
MONGO_PORT = 33423
MONGO_DB = "tsops_dev_db"
MONGO_COLLECTION = "timeseries"

# Create MongoDB client
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB]

@app.post("/forecast", tags=["forecast"])
async def upload_timeseries(
    collection_name: str = f"{fw.generate('p')}_{fw.generate('o')}",
    file: UploadFile = File(...)
):
    contents = await file.read()
    collection = db[collection_name]

    try:
        data = BytesIO(contents)
        df = pd.read_csv(data)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('UTC')
        payload = df.to_dict('records')
    except:
        return {"error": "Error reading file"}

    try:
        collection.insert_many(payload)
        count = collection.count_documents({})
    except:
        return {"error": f"Error uploading data to DB {MONGO_DB} collection {MONGO_COLLECTION}"}
    
    return {"message": f"Successfully uploaded {count} entries into DB {MONGO_DB} collection {MONGO_COLLECTION}"}

@app.post("/create_collection", tags=["forecast"])
async def upload_timeseries(
    collection_name: str = f"{fw.generate('p')}_{fw.generate('o')}",
    time_field: str = "timestamp",
    meta_field: str = "metadata",
    granularity: Literal['hours', 'minutes', 'seconds'] = 'seconds',
    bucketMaxSpanSeconds: int = None,
    bucketRoundingSeconds: int = None,
    expireAfterSeconds: int = None,
):
    try:
        db.create_collection(collection_name, 
                                timeseries={
                                    "timeField":time_field,
                                    "metaField":meta_field,
                                    "granularity":granularity,
                                    "bucketMaxSpanSeconds":bucketMaxSpanSeconds,
                                    "bucketRoundingSeconds":bucketRoundingSeconds
                                },
                                expireAfterSeconds=expireAfterSeconds)
    except pymongo.errors.CollectionInvalid:
        return {"error": f"Collection {collection_name} already exists in DB {MONGO_DB}"}
    except:
        return {"error": f"Error creating collection {collection_name} in DB {MONGO_DB}"}

    return {"message": f"Successfully created collection {collection_name} in DB {MONGO_DB}"}