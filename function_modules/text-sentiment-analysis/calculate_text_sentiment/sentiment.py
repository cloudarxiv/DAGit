from flask import Flask, request, jsonify
import os
import json
import sys
from textblob import TextBlob
import pickle
import time
import uuid  # Import the uuid module
import store_output


import requests

import redis

app = Flask('sentiment')

@app.route('/calculate_sentiment', methods=['POST'])
def main():
    
    try:
        params = request.json
        host = params.get("host")
        port = params.get("port")
        key = params.get("key")
        # # Connect to the Redis instance using the provided host and port
        redis_instance = redis.Redis(host=host, port=port,db=2)
        input = pickle.loads(redis_instance.get(key))
        ##############################################################
        sentences = input["processed_data"]
        sentiments = []
        for sentence in sentences:
            blob = TextBlob(sentence)
            sentiment = blob.sentiment.polarity
            sentiments.append(sentiment)
            
                
        ################################################################################
        
        activation_id = str(uuid.uuid4())

        response = {
        "activation_id": activation_id,
        "sentiments": sentiments
       }
        
        key = store_output.store_intermediate_data(response,'calculate_sentiment','redis')  
    
        response_data={}
        response_data["activation_id"] = activation_id    
        response_data["key"] = key
    
        return jsonify(response_data) # returns key and activation id 

        # # Call the store_data endpoint to store the response
        # store_data_url = "http://10.129.28.219:5005/store_data/calculate_sentiment/redis"
        # # headers = {'Content-Type': 'application/json'}
        # response_store = requests.post(store_data_url,json=response, verify=False)

        # if response_store.status_code == 200:
        #     # If storing the data is successful, print the key
        #     response_data = response_store.json()            
        #     response_data["activation_id"] = activation_id
        # else:
        #     # If there's an error, print the status code
        #     print("Error:", response_store.status_code)

        # return jsonify(response_data)
        # #################################################################################

    except Exception as e:
        # sentences = params["processed_data"]    
        print(json.dumps({ "activation_id": activation_id,
                            "error" : e
                        }))

        return(jsonify({"activation_id": activation_id,
                "error":e
            }))
    
    

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080,threaded=True)
