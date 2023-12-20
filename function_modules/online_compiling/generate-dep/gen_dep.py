#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# Action generate a list of dependencies for a 
# source file, including header files. 

def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  
    
    responses_list = params["__ow_body"]
    
    found_dict = None
    for responses_dict in responses_list:
        if "c_file_url" in responses_dict:
                found_dict = responses_dict
                c_file_url = found_dict["c_file_url"]
                break
     
    found_dict = None

    for responses_dict in responses_list:
        if "stripped_outfile" in responses_dict:
                found_dict = responses_dict
                stripped_outfile = found_dict["stripped_outfile"]
                break
        
    found_dict = None

    for responses_dict in responses_list:
        if "nm_outfile" in responses_dict:
                found_dict = responses_dict
                nm_outfile = found_dict["nm_outfile"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "symbols" in responses_dict:
                found_dict = responses_dict
                nm_symbols = found_dict["symbols"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "ranlib_outfile" in responses_dict:
                found_dict = responses_dict
                ranlib_outfile = found_dict["ranlib_outfile"]
                break
        


    # c_file_url = params["c_file_url"]
    
    source_file = "source_"+activation_id+".c"
    


    output_file = "output_"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        
         # Run 'gcc -MM' to generate dependencies and redirect output to a file
        dependency_file = "source" + activation_id+  ".d"
        dependency_command = f"gcc -MM {source_file} -MF {dependency_file}"

        subprocess.check_call(dependency_command, shell=True)

        # Read the generated dependency file
        with open(dependency_file, 'r') as dep_file:
            dependencies = dep_file.read()

        # Extract dependencies from the output
        dependency_lines = dependencies.splitlines()
        # The first line contains the target, so we skip it
        dependencies = dependency_lines[0:]

        # Remove the temporary dependency file
        os.remove(dependency_file)
        
        print(json.dumps({
            "activation_id": str(activation_id),
            "gen_output": dependency_file,
            "gen-dep": dependencies,
            "c_file_url": c_file_url,
            "stripped_outfile":stripped_outfile,
            "nm_outfile":nm_outfile,
            "nm_symbols":nm_symbols,
            "ranlib_outfile":ranlib_outfile
            
        }))
        return {
            "activation_id": str(activation_id),
            "gen_output": dependency_file,
            "gen-dep": dependencies,
            "c_file_url": c_file_url,
            "stripped_outfile":stripped_outfile,
            "nm_outfile":nm_outfile,
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
