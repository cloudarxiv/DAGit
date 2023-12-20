#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# Ranlib creates an index of the contents of archive_file.a and stores the index in archive_file.a. 
# This is useful for linking and in case the objects call each other

# Usage: ranlib foo.a [ar foo.a foo.o foo1.o foo2.o]

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
        
        # # create an archive
        
        # obj_file = source_file+".o"
        
        # archive = output_file+".a"
        
        # # Create archive - archive a collection of object files
        
        # ar_command = f"ar {archive} {obj_file}"
        
        # subprocess.check_call(ar_command, shell=True)

    
        #
        
        # ranlib_command = f"ranlib  {archive}"

        # # Execute the ranlib command
        # subprocess.check_call(ranlib_command, shell=True)
        
        # Place holder

        print(json.dumps({
            "activation_id": str(activation_id),
            "ranlib_outfile": output_file,
            "c_file_url" : c_file_url
        }))
        return {
            "activation_id": str(activation_id),
            "ranlib_outfile": output_file,
            "c_file_url" : c_file_url
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
