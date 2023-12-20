#!/usr/bin/env python3

import json
import subprocess
import requests
import os

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


    try:
        
        compile_command = f"gcc {source_file} -o {binary_file}"
        
        # Execute the compilation command
        subprocess.check_call(compile_command, shell=True)       
        
        
        readelf_command = f"readelf -a {binary_file}"
        
        # Execute the readelf command
        readelf_output = subprocess.check_output(readelf_command, shell=True).decode()
        
        
        print(json.dumps({
            "activation_id": str(activation_id),
            "readelf_output": readelf_output,            
            "c_file_url": c_file_url,
            "nm_outfile":nm_outfile,
            "gen_dep": gen_output,
            "ranlib_outfile":ranlib_outfile,
            "nm_symbols":nm_symbols
        }))
        return {
            "activation_id": str(activation_id),
            "readelf_output": readelf_output,            
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
