from flask import Flask, request, jsonify
import uuid  # Import the uuid module
import json
from textblob import TextBlob
from newspaper import Article
import redis
import re
import pickle

import requests


app = Flask('fetch_sentences')

@app.route('/fetch_sentences', methods=['POST'])
def main():

    # Get parameters from the POST request
    
    try:
        
        params = request.json
        # If part of an intermediate function in the workflow         
        host = params.get("host")
        port = params.get("port")
        key = params.get("key")
        redis_instance = redis.Redis(host=host, port=port,db=2)
        input = pickle.loads(redis_instance.get(key))        
        url = input["url"]
    except:        
        url = params["url"]
        
    # params = request.json
    # url = params.get("url")

    # Process the article
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    data = article.summary

    # Clean up the data
    data = re.sub(r'\n', ' ', data)
    data = re.sub(r'\[\d+\]', '', data)
    sentences = re.split(r'\.', data)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    
    
    ################################################################################
    
    activation_id = str(uuid.uuid4())
    response = {
        "activation_id": activation_id,
        "processed_data": sentences
    }    
    # Call the store_data endpoint to store the response
    store_data_url = "http://10.129.28.219:5005/store_data/fetch_sentences/redis"
    # headers = {'Content-Type': 'application/json'}
    response_store = requests.post(store_data_url,json=response, verify=False)  # returns the key only

    if response_store.status_code == 200:
        # If storing the data is successful, print the key
        response_data = response_store.json()
        
        response_data["activation_id"] = activation_id

        print("Key:", response_data["key"])
    else:
        # If there's an error, print the status code
        print("Error:", response_store.status_code)

    return jsonify(response_data) # returns key and activation id 
    ################################################################################
    
    
    
   

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)
