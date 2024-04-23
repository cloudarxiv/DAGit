import redis 
from flask import Flask, request, jsonify
import pickle
import minio_dagit
import redis_setup

import uuid

app = Flask('intermediate_store')


@app.route('/store_data/<function_name>/<destination>', methods=['POST'])

def store_intermediate_data(function_name,destination):
    
    data= request.json 
    
    if destination == "redis":
        
        redis_instance = redis_setup.create_redis_master_instance()
                
        redis_instance.set(function_name+"-output",pickle.dumps(data))    
        
        return jsonify({"key": function_name + "-output"})
    
    elif destination == "minio":
        
        bucket_name = 'dagit-store'
        minio_client = minio_dagit.create_minio_client(bucket_name)
        
        unique_id = str(uuid.uuid4())
        
        minio_dagit.write_to_minio(minio_client,data,function_name+'-'+unique_id+'.json',bucket_name)
        
        return jsonify({"key": function_name+'-'+unique_id+'.json'}) 
 

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5005)
