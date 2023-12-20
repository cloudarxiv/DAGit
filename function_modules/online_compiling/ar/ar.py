#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# ar command is used to create, modify and extract the files from the archives.
# An archive is a collection of other files having a particular structure
# from which the individual files can be extracted. 
# Individual files are termed as the members of the archive

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    executable = params["executable"]
    output_executable = params["linker_executable"]
    output_file_object = params["object_files"]
    
    
    
    source_file = "source_"+activation_id+".c"

    output_file = "output_"+activation_id+".o"
    
    ar_output_file = "ar_output"+activation_id+".a"
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        compile_command = f"gcc -o {output_file} {source_file}"
        
        # Execute the compilation command
        subprocess.check_call(compile_command, shell=True)
        
        ar_command = f"ar -crs {ar_output_file} {output_file}"

        # Execute the strip command
        subprocess.check_call(ar_command, shell=True)

        print(json.dumps({
            "activation_id": str(activation_id),
            "ar_outfile": ar_output_file,
            "executable": executable,
            "c_file_url": c_file_url,
            "linker_executable ": output_executable,
            "object_files": output_file_object
        }))
        return {
            "activation_id": str(activation_id),
            "ar_outfile": ar_output_file,
            "executable": executable,
            "c_file_url": c_file_url,
            "linker_executable ": output_executable,
            "object_files": output_file_object
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
