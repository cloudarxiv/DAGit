from functions import Functions
from deployment import DeploymentManager


# provide name of the function
# func = 'fetch_sentences'
# func = 'calculate_sentiment'
# func = 'create_sentiment_report'
# func = 'hello'
# func = 'gpu_test'

func = "check_if_Full"

fr = Functions()

deployment = DeploymentManager(func)

deployment_name = "dagit-deployment-"+deployment.function_name

# deployment.update_deployment_cpu_resources(deployment_name,2,2)

service_name = deployment.function_name
hpa_name = deployment.function_name


# Delete deployment 
deployment.delete_deployment(deployment_name)
deployment.delete_service(service_name)
deployment.delete_hpa(hpa_name)


# Delete function from the store

fr.delete_function(func)
