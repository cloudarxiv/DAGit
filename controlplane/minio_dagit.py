from minio import Minio
from dotenv import load_dotenv
import os
import json
import io


def create_minio_client(bucket_name):
    load_dotenv()
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')
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
