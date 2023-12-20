#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# cc command is stands for C Compiler, usually an alias command to gcc or clang.
# As the name suggests, executing the cc command will usually call the gcc on Linux systems. 
# It is used to compile the C language codes and create executables.

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    
    preprocessed_output = params["preprocessed_output"]
    
    readelf_output = params["readelf_output"]
    
    dir_watcher_output = params["dir_watcher_output"]
    
    gen_dep = params["gen_dep"]
    
    nm_symbols = params["nm_symbols"]
    
    ranlib_outfile = params["ranlib_outfile"]
    
    
    source_file = "source_"+activation_id+".c"

    output_file = "cc_output"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        compile_command = f"cc -o {output_file} {source_file}"
        
        # Execute the compilation command
        subprocess.check_call(compile_command, shell=True)        
        
        print(json.dumps({
            "activation_id": str(activation_id),
            "cc_outfile": output_file,
            "c_file_url": c_file_url,
            "preprocessed_output": preprocessed_output,
            "readelf_output": readelf_output,
            "dir_watcher_output":dir_watcher_output,
            "gen_dep":gen_dep,
            "nm_symbols":nm_symbols,
            "ranlib_outfile":ranlib_outfile
            
        }))
        return {
            "activation_id": str(activation_id),
            "cc_outfile": output_file,
            "c_file_url": c_file_url,
            "preprocessed_output": preprocessed_output,
            "readelf_output": readelf_output,
            "dir_watcher_output":dir_watcher_output,
            "gen_dep":gen_dep,
            "nm_symbols":nm_symbols,
            "ranlib_outfile":ranlib_outfile
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
