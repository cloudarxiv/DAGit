#!/usr/bin/env python3
import os
import redis
import pickle
import subprocess
import time
import json
import requests
import sys

from botocore.exceptions import ClientError


from urllib.request import urlopen,urlretrieve

# provides an abstraction to user

def main(params):
    
    activation_id = os.environ.get('__OW_ACTIVATION_ID')     
    
    c_file_url = params["c_file_url"]
    
    # source_file = "source_"+activation_id+".c"

    # output_file = "output_"+activation_id+"-output"
    
    # response = requests.get(c_file_url)
    # if response.status_code == 200:
    #     with open(source_file, 'wb') as f:
    #         f.write(response.content)

    

    # compile_command = f"gcc -o {output_file} {source_file}"
        
    # # Execute the compilation command
    # subprocess.check_call(compile_command, shell=True)
    
    
    print(json.dumps({"activation_id": str(activation_id),
                      "c_file_url" : c_file_url

                    }))

    return({"activation_id": str(activation_id),
            "c_file_url" : c_file_url
        })       
    

   
            

if __name__ == "__main__":
    main(params)