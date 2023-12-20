#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# Linker links a list of object files to create an executable

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    
    assembly_source = params["assembly_source_file"]
    
    assembly_output_file = params["assembly_output"]
    
    preprocessed_output = params["preprocessed_output"]
    
    readelf_output = params["readelf_output"]
    
    dir_watcher_output = params["dir_watcher_output"]
    
    gen_dep = params["gen_dep"]
    
    nm_symbols = params["nm_symbols"]
    
    ranlib_outfile = params["ranlib_outfile"]   
    
    
    source_file = "source_"+activation_id+".c"    


    output_executable = "linker_output_executable"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)
            
    output_file = "linker_object_"+activation_id+".o"


    obj_files_list = []
    try:
        # for i in range(3): # Simulating 3 object files for linking 
            
        #     output_file = "linker_object_"+i+".o"

        #     # compile_command = f"gcc -o {output_file} {source_file}"
            
        #     # subprocess.check_call(compile_command, shell=True)

            
        #     obj_files_list.append(output_file)
        
        
        
        
        
        # link_command = f"gcc -o {object_file} {output_executable}"       

        # subprocess.check_call(link_command, shell=True)
        
        
        
        print(json.dumps({
            "activation_id": str(activation_id),
            "linker_executable": output_executable,
            "object_files": output_file,
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
            "linker_executable": output_executable,
            "object_files": output_file,
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
