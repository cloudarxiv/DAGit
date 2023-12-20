#!/usr/bin/env python3

import json
import subprocess
import requests
import os
import time

# When we compile source code, an object file is generated of the program
# and with the help of linker, this object files gets converted to a binary
# file which, only the machine can understand.
# This kind of file follows some structures one of which is ELF(Executable and Linkable Format).
# And to get the information of these ELF files readelf command is used.


def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    
    
    nm_outfile = params["nm_outfile"]
    
    gen_output = params["gen_output"]
    
    ranlib_outfile = params["ranlib_outfile"]
    
    nm_symbols = params["nm_symbols"]
    
    source_file = "source_"+activation_id+".c"   
    

    binary_file = "elf_file"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)

    compile_directory = 'test-directory'
    try:
        
        if not os.path.exists(compile_directory):
            os.makedirs(compile_directory)     
        
        # Create the destination file path in the target directory
        destination_file_path = os.path.join(compile_directory, os.path.basename(source_file))
        
        # Move the source file to the target directory
        os.rename(source_file, destination_file_path)


        
        print(json.dumps({
            "activation_id": str(activation_id),
            "dir_watcher_output": destination_file_path,            
            "c_file_url": c_file_url,
            "nm_outfile":nm_outfile,
            "gen_dep": gen_output,
            "ranlib_outfile":ranlib_outfile,
            "nm_symbols":nm_symbols
        }))
        return {
            "activation_id": str(activation_id),
            "dir_watcher_output": destination_file_path,            
            "c_file_url": c_file_url,
            "nm_outfile":nm_outfile,
            "gen_dep": gen_output,
            "ranlib_outfile":ranlib_outfile,
            "nm_symbols":nm_symbols
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
