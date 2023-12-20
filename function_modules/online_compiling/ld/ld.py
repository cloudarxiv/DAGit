#!/usr/bin/env python3

import json
import subprocess
import requests
import os

# This  ld uses the general purpose BFD libraries to operate on object files.
# This allows ld to read, combine, and write object files in many 
# different formats: for example, COFF or "a.out". 
# Different formats may be linked together to produce any 
# available kind of object file.


def main(params):
        
    activation_id = os.environ.get('__OW_ACTIVATION_ID')  

    c_file_url = params["c_file_url"]
    output_executable = params["linker_executable"]
    output_file = params["object_files"] 
    
    
    
    
    source_file = "source_"+activation_id+".c"   
    
    executable = "ld_executable_"+activation_id
    
    response = requests.get(c_file_url)
    if response.status_code == 200:
        with open(source_file, 'wb') as f:
            f.write(response.content)


    try:
        
        # link_command = ["ld", "-o", output_executable] + object_files

        # # Execute the linker command
        # subprocess.check_call(link_command)
        
        output_file_1 = "output_1.o"
        
        compile_command_1 = f"gcc -o {output_file_1} {source_file}"
        
        # Execute the compilation command
        subprocess.check_call(compile_command_1, shell=True)
        
        output_file_2 = "output_2.o"
        
        compile_command_2 = f"gcc -o {output_file_2} {source_file}"
        
        # Execute the compilation command
        subprocess.check_call(compile_command_2, shell=True)
        
        # ld -o my_program file1.o file2.o

        
        ld_command = f"ld -o {executable} {output_file_1} {output_file_2}"
        
        subprocess.check_call(ld_command, shell=True)





        print(json.dumps({
            "activation_id": str(activation_id),
            "ld_output": [output_file_1,output_file_2],
            "executable": executable,
            "c_file_url": c_file_url,
            "linker_executable": output_executable,
            "object_files": output_file
        }))
        return {
            "activation_id": str(activation_id),
            "ld_output": [output_file_1,output_file_2],
            "executable": executable,
            "c_file_url": c_file_url,
            "linker_executable": output_executable,
            "object_files": output_file
        }
    except subprocess.CalledProcessError as e:
        return {
            "activation_id": str(activation_id),
            "error": str(e)
        }
        
if __name__ == "__main__":
    main(params)
