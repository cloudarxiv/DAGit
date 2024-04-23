from flask import Flask, request, jsonify
import os
import json
import sys
import re
import pandas as pd
import time
import redis
import pickle
import uuid  # Import the uuid module

import requests

app = Flask('sentiment_report')

@app.route('/create_sentiment_report', methods=['POST'])
def main():
    
    
    params = request.json      
    host = params["host"]
    port = params["port"]
    keys = params["key"]
    input_list = []
        
    try:
        
        # Connect to the Redis instance using the provided host and port
        redis_instance = redis.Redis(host=host, port=port,db=2)
        for key in keys:
            input_list.append(pickle.loads(redis_instance.get(key)))
        ##############################################################
        
        sentences = input_list[0]["processed_data"]
        sentiments = input_list[1]["sentiments"]
        # sentences = params["__ow_body"][0]["processed_data"]
        # sentiments = params["__ow_body"][1]["sentiments"]        
        # Combine sentences and sentiments into a list of dictionaries
        data = [{"Sentence": sentence, "Sentiment": sentiment} for sentence, sentiment in zip(sentences, sentiments)]

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)

        # Convert DataFrame to a formatted string with cleaned formatting
        report = df.to_string(index=False)
        report = re.sub(r'\n +', '\n', report)
        report = report.strip()    
        
        ################################################################################
        activation_id = str(uuid.uuid4())

        response = { "activation_id": str(activation_id),
                    "report" : report
                    }
        
        return jsonify(response)
    
        # # Call the store_data endpoint to store the response
        # store_data_url = "http://10.129.28.219:5005/store_data/create_sentiment_report/redis"
        # # headers = {'Content-Type': 'application/json'}
        # response_store = requests.post(store_data_url,json=response, verify=False)

        # if response_store.status_code == 200:
        #     # If storing the data is successful, print the key
        #     response_data = response_store.json()
        #     response_data["activation_id"] = activation_id

        #     print("Key:", response_data["key"])
        # else:
        #     # If there's an error, print the status code
        #     print("Error:", response_store.status_code)

        # return jsonify(response_data)
        # #################################################################################
        
        # print(json.dumps(response))
        # return jsonify(response)
    
    except Exception as e:
        sentences = params["processed_data"]    
        print(json.dumps({ "activation_id": str(activation_id),
                            "error" : e
                        }))

        return({"activation_id": str(activation_id),
                "error":e
            })
    

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080,threaded=True)
