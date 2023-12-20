#!/usr/bin/env python3

import pymongo

def get_trigger_json(trigger_name):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["trigger_store"]
    mycol = mydb["triggers"]
    query = {"trigger_name":trigger_name}
    projection = {"_id": 0, "trigger_name": 1,"type": 1,"dags": 1, "functions":1}
    document = mycol.find(query, projection)
    data = list(document)
    return data


