import pymongo
from loguru import logger
import pandas as pd


class Database:
    def __init__(self, cfg):
        self.cfg = cfg     
        self.client = pymongo.MongoClient(self.cfg["mongo_url"])
        self.collection = self.client.self.cfg["db_name"][self.cfg["collection"]]
        
    def get_last_update(self):
        data = self.collection.find_one({'timestamp': {'$exists': True}}, sort=[('timestamp', pymongo.DESCENDING)])
        return data

    def get_daily_data(self, from_date, to_date):
        from_date = from_date.replace(tzinfo=None)  
        to_date = to_date.replace(tzinfo=None)
        data = self.collection.find({"timestamp": {"$gte": from_date, "$lt": to_date}})
        data = pd.DataFrame(data)            
        if len(data) > 0:
            data.drop(columns=["_id"], inplace=True)
            data.sort_values(by=['timestamp'], inplace=True)
        return data

    def get_last_hour_data(self, from_date, to_date):
        from_date = from_date.replace(tzinfo=None)  
        to_date = to_date.replace(tzinfo=None)
        data = self.collection.find({"timestamp": {"$gte": from_date, "$lt": to_date}})
        data = pd.DataFrame(data)            
        if len(data) > 0:
            data.drop(columns=["_id"], inplace=True)
            data.sort_values(by=['timestamp'], inplace=True)
        
        return data
