import subprocess
import time

# Command to execute
command = 'wsk -i action invoke toonify --result --param-file ../function_modules/decode-function/params.json'

# Number of iterations
num_iterations = 20

# Log file path
log_file = "execution_log_composer.txt"

# Perform command execution and calculate execution time
with open(log_file, "w") as file:
    file.write("Request Command\tExecution Time\n")

    for _ in range(num_iterations):
        start_time = time.time()
        subprocess.run(command, shell=True)
        end_time = time.time()

        execution_time = end_time - start_time

        file.write(f"{command}\t{execution_time:.6f} seconds\n")
