#!/usr/bin/env python3

import os
import json
import sys
from textblob import TextBlob
from newspaper import Article
import re


def main(params):
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    # params = json.loads(sys.argv[1])
    url = params["url"]
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    data = article.summary

    # Remove newlines and numbers in square brackets
    data = re.sub(r'\n', ' ', data)
    data = re.sub(r'\[\d+\]', '', data)

    # Split summary into sentences based on periods
    sentences = re.split(r'\.', data)
    
    # Remove leading/trailing whitespaces and empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    print(json.dumps({ "activation_id": str(activation_id),
                        "processed_data" : sentences
                    }))

    return({"activation_id": str(activation_id),
            
            "processed_data":sentences
        })
    
    

if __name__ == "__main__":
    main(params)
