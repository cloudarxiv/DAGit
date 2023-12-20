#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# Preprocessor is just a text substitution tool 
# and it instructs the compiler to do required pre-processing
# before the actual compilation.

# define MAX_ARRAY_LENGTH 20 - tells the program to replace instances of MAX_ARRAY_LENGTH with 20
# include, define, ifdef

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID') 
    
    
    responses_list = params["__ow_body"]
    
    
    # readelf_output = params["__ow_body"][0]["readelf_output"]
    
    # dir_watcher_output = params["__ow_body"][1]["dir_watcher_output"]

    # nm_symbols = params["__ow_body"][0]["nm_symbols"]
    
    # gen_dep = params["__ow_body"][0]["gen_dep"]
    
    # ranlib_outfile = params["__ow_body"][0]["ranlib_outfile"]
    
    # c_file_url = params["__ow_body"][0]["c_file_url"]

    
    found_dict = None
    for responses_dict in responses_list:
        if "readelf_output" in responses_dict:
                found_dict = responses_dict
                readelf_output = found_dict["readelf_output"]
                break
     
    found_dict = None

    for responses_dict in responses_list:
        if "dir_watcher_output" in responses_dict:
                found_dict = responses_dict
                dir_watcher_output = found_dict["dir_watcher_output"]
                break
        
    found_dict = None

    for responses_dict in responses_list:
        if "nm_symbols" in responses_dict:
                found_dict = responses_dict
                nm_symbols = found_dict["nm_symbols"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "gen_dep" in responses_dict:
                found_dict = responses_dict
                gen_dep = found_dict["gen_dep"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "ranlib_outfile" in responses_dict:
                found_dict = responses_dict
                ranlib_outfile = found_dict["ranlib_outfile"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "c_file_url" in responses_dict:
                found_dict = responses_dict
                c_file_url = found_dict["c_file_url"]
                break
        

    # c_file_url = params["c_file_url"]
    
    source_file = "source_"+activation_id+".c"   
    

    output_file = "preprocssed_output_"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        
        preprocess_command = f"gcc -E {source_file} -o {output_file}"
        
        # Execute the preprocessing command
        subprocess.check_call(preprocess_command, shell=True)
        
        print(json.dumps({
            "activation_id": str(activation_id),
            "preprocessed_output": output_file,            
            "c_file_url": c_file_url,
            "readelf_output": readelf_output,
            "dir_watcher_output":dir_watcher_output,
            "nm_symbols":nm_symbols,
            "gen_dep":gen_dep,
            "ranlib_outfile":ranlib_outfile
            
        }))
        return {
            "activation_id": str(activation_id),
            "preprocessed_output": output_file,            
            "c_file_url": c_file_url,
            "readelf_output": readelf_output,
            "dir_watcher_output":dir_watcher_output,
            "nm_symbols":nm_symbols,
            "gen_dep":gen_dep,
            "ranlib_outfile":ranlib_outfile
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
