import redis 
from flask import Flask, request, jsonify
import pickle
from minio import Minio
from dotenv import load_dotenv
import uuid
import json
import io
import os 

def create_redis_master_instance():   
    try:  
        r = redis.Redis(host="10.104.98.1", port=6379, db=2) # connect to ClusterIP redis service on  6379
        print("Role:",r.info()['role'])
        return r
    except Exception as e:
        print("Error-",e)
        
        
def create_minio_client(bucket_name):
    load_dotenv()
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # print(ACCESS_KEY)
    # print(SECRET_KEY)
    MINIO_API_HOST = "http://localhost:9000"
    MINIO_CLIENT = Minio("localhost:9000", access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
    # Check if the bucket exists, if not create it
    found = MINIO_CLIENT.bucket_exists(bucket_name)
    if not found:
        MINIO_CLIENT.make_bucket(bucket_name)
    else:
        print("Bucket already exists")
        
    return MINIO_CLIENT

def write_to_minio(client,json_data,filename,bucket_name):
    
    try:

        # Convert JSON data to string
        json_str = json.dumps(json_data)

        # Convert the string to bytes
        json_bytes = json_str.encode('utf-8')

        # Wrap the bytes data in a BytesIO object
        data_stream = io.BytesIO(json_bytes)

        # Upload the JSON data to MinIO
        client.put_object(bucket_name, filename, data_stream, len(json_bytes), 'application/json')

        # print("JSON data successfully uploaded to MinIO bucket")
        
    except Exception as e:
        print("Error----------------",e)


def store_intermediate_data(data, function_name,destination):
    
    # data= request.json 
    
    if destination == "redis":
        
        redis_instance = create_redis_master_instance()
        
        key = function_name+"-output"
                
        redis_instance.set(key,pickle.dumps(data))
        
        return key
        
        # return jsonify({"key": function_name + "-output"})
    
    elif destination == "minio":
        
        bucket_name = 'dagit-store'
        minio_client = create_minio_client(bucket_name)
        
        unique_id = str(uuid.uuid4())
        
        key = function_name+'-'+unique_id+'.json'
        
        write_to_minio(minio_client,data,key,bucket_name)
        
        return key
        
        # return jsonify({"key": function_name+'-'+unique_id+'.json'}) 
 
