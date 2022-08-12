import numpy as np
import pandas as pd
from fastapi import FastAPI
from s2cell import s2cell
from sklearn.neighbors import KDTree

from mongoutil import MongoConnector
from collections import OrderedDict
from geopy import distance

RESULT_COUNT = 5

app = FastAPI()
client = MongoConnector.connect()
collection = client.hawker.dataset


@app.get("/")
async def root():
    return {"message": "Welcome to Hawker Finder API"}


@app.get("/find/v1")
async def find_near_by_hawker_centre_v1(latitude: float = None, longitude: float = None):
    """Using Google S2 cells search and sort by distance"""
    # available_zones = [20, 19, 17, 16, 15, 14, 13, 12, 11, 10]
    search_by_zones = [14, 13, 12, 11, 10, 9]

    total_records = OrderedDict()
    no_of_zones_searched = 0

    for zone in search_by_zones:
        zone_key = f"ZONE_{zone}"
        s2cell_val = s2cell.lat_lon_to_cell_id(latitude, longitude, zone)
        projection = {"_id": False, "NAME": True, "ADDRESS": True, "PHOTOURL": True, "LAT": True, "LONG": True}
        res = collection.find({zone_key: s2cell_val}, projection)
        records = list(res)

        for rec in records:
            if rec.get("NAME") not in total_records:
                total_records[rec.get("NAME")] = rec

        no_of_zones_searched += 1
        if len(total_records) >= RESULT_COUNT:
            break

    near_by_records = list(total_records.values())

    for rec in near_by_records:
        dist = distance.distance((rec.get("LAT"), rec.get("LONG")), (latitude, longitude))
        rec['dist'] = {"m": dist.m, "km": dist.km, "miles": dist.miles}
    near_by_records.sort(key=lambda x: x['dist']['m'], reverse=False)
    return near_by_records[:RESULT_COUNT]


@app.get("/find/v2")
async def find_near_by_hawker_centre_v2(latitude: float = None, longitude: float = None):
    """Fetch All rows & compute distance with geopy distance, sort and return n records"""
    projection = {"_id": False, "NAME": True, "ADDRESS": True, "PHOTOURL": True, "LAT": True, "LONG": True}
    res = collection.find({}, projection)
    all_records = list(res)
    for rec in all_records:
        dist = distance.distance((rec.get("LAT"), rec.get("LONG")), (latitude, longitude))
        rec['dist'] = {"m": dist.m, "km": dist.km, "miles": dist.miles}
    all_records.sort(key=lambda x: x['dist']['m'], reverse=False)
    return all_records[:RESULT_COUNT]


@app.get("/find/v3")
async def find_near_by_hawker_centre_v3(latitude: float = None, longitude: float = None):
    """Using KDTree: Fetch All rows, Build KDTree & query n neighbour records"""
    projection = {"_id": False, "NAME": True, "ADDRESS": True, "PHOTOURL": True, "LAT": True, "LONG": True}
    res = collection.find({}, projection)
    all_records = list(res)
    cords = np.array([[rec.get("LAT"), rec.get("LONG")] for rec in all_records])
    tree = KDTree(cords, leaf_size=2)
    dist, ind = tree.query(np.array([[latitude, longitude]]), k=RESULT_COUNT)
    result = pd.Series(all_records).iloc[ind[0]].values.tolist()
    return result

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
