from fastapi import FastAPI
from s2cell import s2cell
from mongoutil import MongoConnector

RESULT_COUNT = 5

app = FastAPI()
client = MongoConnector.connect()
collection = client.hawker.dataset


@app.get("/")
async def root():
    return {"message": "Welcome to Hawker Finder API"}

@app.get("/find")
async def find_near_by_hawker_centre(latitude: float = None, longitude: float = None):
    
    # available_zones = [20, 19, 17, 16, 15, 14, 13, 12, 11, 10]
    search_by_zones = [14, 13, 12, 11, 10, 9]

    total_records = []
    no_of_zones_searched = 0

    for zone in search_by_zones:
        zone_key = f"ZONE_{zone}"
        s2cell_val = s2cell.lat_lon_to_cell_id(latitude, longitude, zone)
        projection = {"_id": False, "NAME": True, "ADDRESS": True, "PHOTOURL": True, "LAT": True, "LONG": True}
        res = collection.find({zone_key: s2cell_val}, projection)
        records = list(res)

        if len(records) > 0:
            total_records.extend(records)

        no_of_zones_searched += 1
        if len(total_records) >= RESULT_COUNT:
            break

    print(no_of_zones_searched)
    return total_records
