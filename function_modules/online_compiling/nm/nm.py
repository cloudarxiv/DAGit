#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# The nm command displays information about symbols
# in the specified File, which can be an object file,
# an executable file

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
        
        # List symbols in the binary
        nm_command = f"nm {output_file}"

        # Execute the nm command
        symbols = subprocess.check_output(nm_command, shell=True).decode()

        
        print(json.dumps({
            "activation_id": str(activation_id),
            "nm_outfile": output_file,
            "symbols": symbols,
            "c_file_url" : c_file_url
        }))
        return {
            "activation_id": str(activation_id),
            "nm_outfile": output_file,
            "symbols": symbols,
            "c_file_url" : c_file_url
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
