#!/usr/bin/env python3

import os
import json
import sys
import re
import pandas as pd



def main(params):
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    
    sentences = params["__ow_body"][0]["processed_data"]

    sentiments = params["__ow_body"][1]["sentiments"]
    
    # Combine sentences and sentiments into a list of dictionaries
    data = [{"Sentence": sentence, "Sentiment": sentiment} for sentence, sentiment in zip(sentences, sentiments)]

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Convert DataFrame to a formatted string with cleaned formatting
    report = df.to_string(index=False)
    report = re.sub(r'\n +', '\n', report)
    report = report.strip()
    
    
    print(json.dumps({ "activation_id": str(activation_id),
                        "report" : report
                    }))

    return({"activation_id": str(activation_id),
            "report":report
        })
    
    

if __name__ == "__main__":
    main(params)
