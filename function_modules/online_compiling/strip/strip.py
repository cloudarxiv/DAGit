#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# The strip command is a GNU utility that is used
# to remove unnecessary information from the compiled file,
# reducing its size

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    
    source_file = "source_"+activation_id+".c"

    output_file = "output_"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        compile_command = f"gcc -o {output_file} {source_file}"
        
        # Execute the compilation command
        subprocess.check_call(compile_command, shell=True)
        
        strip_command = f"strip -s {output_file}"

        # Execute the strip command
        subprocess.check_call(strip_command, shell=True)

        print(json.dumps({
            "activation_id": str(activation_id),
            "stripped_outfile": output_file,
            "c_file_url" : c_file_url
            
        }))
        return {
            "activation_id": str(activation_id),
            "stripped_outfile": output_file,
            "c_file_url" : c_file_url
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
