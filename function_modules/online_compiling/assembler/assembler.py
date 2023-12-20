#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# The as command is used to assemble assembly language source files 
# and create executable object files.

# input_source_file = "input_source.s"
# output_object_file = "output_object.o"

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    
    source_file = "source_"+activation_id+".c"
    
    assembly_source = "assembly_"+activation_id+".s"

    assembly_output_file = "assembly_output"+activation_id+".o"
    
    preprocessed_output =  params["preprocessed_output"]
    
    readelf_output = params["readelf_output"]
    
    dir_watcher_output = params["dir_watcher_output"]
    
    gen_dep = params["gen_dep"]    
    
    nm_symbols = params["nm_symbols"]
    
    ranlib_outfile = params["ranlib_outfile"]   
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        
        compile_command = f"gcc -S {source_file} -o  {assembly_source}"
        
        # Execute the compilation command
        
        subprocess.check_call(compile_command, shell=True)
        
        
        assemble_command = f'as -o {assembly_output_file} {assembly_source}'

        # Execute the assembler command
        subprocess.check_call(assemble_command, shell=True)
        
        
        print(json.dumps({
            "activation_id": str(activation_id),
            "assembly_source_file": assembly_source,
            "assembly_output": assembly_output_file,
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
            "assembly_source_file": assembly_source,
            "assembly_output": assembly_output_file,
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
