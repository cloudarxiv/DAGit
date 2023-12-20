#!/usr/bin/env python3

import os
import json
import sys
from textblob import TextBlob


def main(params):
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    # params = json.loads(sys.argv[1])
    sentences = params["processed_data"]
    sentiments = []
    for sentence in sentences:
        blob = TextBlob(sentence)
        sentiment = blob.sentiment.polarity
        sentiments.append(sentiment)

    
    
    print(json.dumps({ "activation_id": str(activation_id),
                        "sentiments" : sentiments
                    }))

    return({"activation_id": str(activation_id),
            "sentiments":sentiments
        })
    
    

if __name__ == "__main__":
    main(params)
