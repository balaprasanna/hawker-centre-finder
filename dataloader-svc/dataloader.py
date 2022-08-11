import pandas as pd
import geopandas as gpd
from bs4 import BeautifulSoup
from s2cell import s2cell
from mongoutil import MongoConnector


class ProcessGeoJsonFile:

    def __init__(self, msg):
        self.msg = msg

    def execute(self):
        self.validate_input_msg()
        data = self.extract_data_from_geo_json_file()
        self.push_to_data_store(data)

    def validate_input_msg(self):
        assert "file_url" in self.msg, "Error: File Not Found in input message"

    def extract_data_from_geo_json_file(self):
        # load geo_json file
        gdf = gpd.read_file(self.msg.get("file_url"))

        lat_long = ['LAT', 'LONG']
        gdf.loc[:, lat_long] = gdf.apply(self.extract_lat_long_from_point, axis=1)

        # add zone info for lat/long
        # refer for cell_stats: https://s2geometry.io/resources/s2cell_statistics.html
        # increasing order from 77 m2, 300 m2, ...0.3 km2, 1.2 km2, 5.0 km2, 20 km2,  81 km2
        zone_levels = [20, 19, 17, 16, 15, 14, 13, 12, 11, 10, 9,8]
        zone_cols = [f"ZONE_{zo}" for i,zo in enumerate(zone_levels)]
        gdf.loc[:, zone_cols] = gdf.apply(self.convert_lang_long_to_s2cells, axis=1, args=(zone_levels,))

        # extract meta data from html content
        keys_to_filter = ['NAME', 'PHOTOURL', 'ADDRESS_MYENV']
        gdf.loc[:, keys_to_filter] = gdf.Description.apply(
            lambda x: self.extract_cols_from_dict(cont_dct=self.html_table_to_dict(x), keys=keys_to_filter))

        # filter relevant columns
        relevant_columns = keys_to_filter + lat_long + zone_cols
        out_df = gdf[relevant_columns].rename(columns={'ADDRESS_MYENV': 'ADDRESS'})
        return out_df

    # util methods for pandas apply func
    @staticmethod
    def convert_lang_long_to_s2cells(s, levels):
        return pd.Series({f"ZONE_{level}": s2cell.lat_lon_to_cell_id(s.LAT, s.LONG, level=level) for i,level in enumerate(levels)})

    @staticmethod
    def extract_lat_long_from_point(p):  # p.y - lat, p.x - long
        return pd.Series({"LAT": p["geometry"].y, "LONG": p["geometry"].x})

    @staticmethod
    def html_table_to_dict(content):
        output_dct = {}
        soup = BeautifulSoup(content, features="lxml")
        for tr in soup.find_all("tr"):
            key = tr.find("th").text
            val = tr.find("td")
            safe_val = val.text if val else val
            output_dct[key] = safe_val
        return output_dct

    @staticmethod
    def extract_cols_from_dict(cont_dct, keys):
        return pd.Series({key: cont_dct.get(key) for key in keys})

    def push_to_data_store(self, df):
        client = MongoConnector.connect()
        db = client.hawker
        collection = db.dataset

        for idx, row in df.iterrows():
            row_dct = row.to_dict()
            res = collection.update_one({"NAME": row.NAME}, {"$set": row_dct}, upsert=True)
            print("SAVED", row_dct)
            print("RESP", res.acknowledged, res.matched_count, res.modified_count)

        client.close()


if __name__ == '__main__':
    msg = {
        #"file_url": "/home/prasanna/Downloads/hawker-centres/hawker-centres-geojson.geojson"
        "file_url": "/Users/balaprasanna/Downloads/hawker-centres/hawker-centres-geojson.geojson"
    }
    ProcessGeoJsonFile(msg).execute()

