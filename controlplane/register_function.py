
from functions import Functions
from deployment import DeploymentManager


fr = Functions() 

# fn = 'anubhav'

# print(fr.get_function('fetch_sentences')) 

# try:
    
#     if(fr.get_function(fn)):
#         print("Present Already")
#     else:
#         print("Not present")

# except Exception as e:
#     print("Not present")
    
# func = fr.register_function("/home/faasapp/Desktop/anubhav/function_modules/gpu_workflow/gpu_test.py","gpu_test","10.129.28.219:5000/gpu_test","gpu")

func = fr.register_function("/home/faasapp/Desktop/anubhav/function_modules/fill_glass_water/glass_full/glass_full.py","glass_full","10.129.28.219:5000/glass_full","cpu")


deployment = DeploymentManager(func)
print("-------------------------DEPL0YMENT OBJECT CREATED -----------------------------------------")
deployment.create_deployment()
print("-------------------------DEPL0YMENT CREATE FINISHED -----------------------------------------")
node_port = deployment.create_service()
print(f"NodePort for service '{func}' is {node_port}")
print("-------------------------SERVICE CREATE FINISHED ----------------------------------------")
deployment.set_autoscaling(min_replicas=1, max_replicas=70)  # Set min and max replicas

