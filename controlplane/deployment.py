from kubernetes import client, config
from kubernetes.client.rest import ApiException
from datetime import datetime, timedelta
import random

import json
import os
from functions import Functions

global function_service_mapping
function_service_mapping = {}

host_ips = ['10.129.28.219','10.129.28.158','10.129.27.94','10.129.28.70','10.129.27.113','10.129.2.187','10.129.2.188','10.129.2.21','10.129.131.194']

class DeploymentManager:
    def __init__(self, function_name):
        self.fname = function_name
        self.function_name = function_name.lower().replace("_", "-")
        self.functions = Functions()
        self.function = json.loads(self.functions.get_function(function_name))
        if not self.function:
            raise ValueError(f"Function '{function_name}' not found in MongoDB.")
        
        
    def get_existing_deployment(self):
        config.load_kube_config()
        # Get list of Deployments in the namespace
        api_instance = client.AppsV1Api()
        deployments = api_instance.list_namespaced_deployment(namespace="default")
        
        # Check if a Deployment with the specific name exists
        for deployment in deployments.items:
            if deployment.metadata.name == "dagit-deployment-" + self.function_name:
                return deployment
        return None
    
    def get_existing_service(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        services = api_instance.list_namespaced_service(namespace="default")
        
        for service in services.items:
            if service.metadata.name == self.function_name:
                return service
        return None
    
    def get_existing_hpa(self):
        api_instance = client.AutoscalingV1Api()
        hpas = api_instance.list_namespaced_horizontal_pod_autoscaler(namespace="default")
        for hpa in hpas.items:
            if hpa.metadata.name == self.function_name:
                return hpa
        return None
    
    # Function creates a deployment 
    def create_deployment(self):
        config.load_kube_config()
        existing_deployment = self.get_existing_deployment()
        if existing_deployment:
            print(f"Deployment for function '{self.function_name}' already exists.")
            return 
        else:
            script_content = self.function["script_content"]
            docker_image = self.function["docker_image"]
            function_type = self.function["type"]
            
            print("Function Type (CPU / GPU): ",function_type)

            if not script_content or not docker_image:
                raise ValueError(f"Script content or Docker image not found for function '{self.function_name}'.")

            resources = client.V1ResourceRequirements(
                requests={"cpu": "2000m"},  # Default CPU resources
                limits={"cpu": "2000m"}
            )

            # Check if function type is GPU and adjust resources and node selector accordingly
            if function_type == "gpu":
                # resources = client.V1ResourceRequirements(
                # requests={"cpu": "500m","nvidia.com/gpu": "1"},  # Request 1 GPU
                # limits={"cpu": "1000m","nvidia.com/gpu": "1"}  # Limit 1 GPU
                # )
                resources = client.V1ResourceRequirements(
                requests={"cpu": "500m"},  # Request 1 GPU
                limits={"cpu": "1000m"}  # Limit 1 GPU
                )

                node_selector_key = "type"
                node_selector_value = "gpu"
            else:
                node_selector_key = "type"
                node_selector_value = "cpu"

            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name="dagit-deployment-"+self.function_name),
                spec=client.V1DeploymentSpec(
                    selector=client.V1LabelSelector(match_labels={"app": self.function_name.lower()}),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={"app": self.function_name.lower()}),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=self.function_name,
                                    image=docker_image,
                                    resources=resources,
                                    ports=[client.V1ContainerPort(container_port=8080)]
                                )
                            ],
                            affinity=client.V1Affinity(
                                node_affinity=client.V1NodeAffinity(
                                    required_during_scheduling_ignored_during_execution=client.V1NodeSelector(
                                        node_selector_terms=[
                                            client.V1NodeSelectorTerm(
                                                match_expressions=[
                                                    client.V1NodeSelectorRequirement(
                                                        key=node_selector_key,
                                                        operator="In",
                                                        values=[node_selector_value]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                )
                            )
                        )
                    )
                )
            )

            apps_api = client.AppsV1Api()
            apps_api.create_namespaced_deployment(namespace="default", body=deployment)
            print("Deployment created successfully.")
            
    # Function updates an exisiting deployment with cpu resource and limit dynamically
    def update_deployment_cpu_resources(self,deployment_name, cpu_request=None, cpu_limit=None):
        config.load_kube_config()

        # Create an instance of the Kubernetes AppsV1Api
        apps_api = client.AppsV1Api()

        try:
            # Retrieve the deployment
            deployment = apps_api.read_namespaced_deployment(name=deployment_name, namespace="default")

            # Update resource requests and limits if provided
            if cpu_request is not None:
                for container in deployment.spec.template.spec.containers:
                    container.resources.requests["cpu"] = cpu_request
            if cpu_limit is not None:
                for container in deployment.spec.template.spec.containers:
                    container.resources.limits["cpu"] = cpu_limit

            # Apply the changes to the deployment
            apps_api.patch_namespaced_deployment(name=deployment_name, namespace="default", body=deployment)
            print(f"CPU resources updated successfully for deployment '{deployment_name}'.")
        except Exception as e:
            print(f"Error updating CPU resources for deployment '{deployment_name}': {e}")


    def delete_deployment(self, deployment_name):
        try:
            # Load Kubernetes configuration
            config.load_kube_config()

            # Create Kubernetes API client
            api_instance = client.AppsV1Api()

            # Delete the deployment
            api_instance.delete_namespaced_deployment(name=deployment_name, namespace="default")

            print(f"Deployment '{deployment_name}' deleted successfully.")
        except ApiException as e:
            print(f"Exception when calling AppsV1Api->delete_namespaced_deployment: {e}")

    
    def set_autoscaling(self, min_replicas, max_replicas):
        # Load Kubernetes configuration
        config.load_kube_config()
        existing_hpa = self.get_existing_hpa()
        if existing_hpa:
            print(f"HPA '{self.function_name}' already exists.")
            return 
        else:
            # Define HorizontalPodAutoscaler object
            autoscaler = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",  # Change to autoscaling/v1
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(name=self.function_name),
                spec=client.V1HorizontalPodAutoscalerSpec(
                    min_replicas=min_replicas,
                    max_replicas=max_replicas,
                    scale_target_ref=client.V1CrossVersionObjectReference(
                        api_version="apps/v1",
                        kind="Deployment",
                        name="dagit-deployment-"+self.function_name
                    ),
                    target_cpu_utilization_percentage=80  # Set target CPU utilization percentage
                )
            )

            # Create the HorizontalPodAutoscaler
            autoscaling_api = client.AutoscalingV1Api()
            autoscaling_api.create_namespaced_horizontal_pod_autoscaler(namespace="default", body=autoscaler)
            print("Autoscaling configured successfully.")
            
    def update_hpa(self, hpa_name, new_min_replica, new_max_replicas):
        # Load Kubernetes configuration
        config.load_kube_config()

        # Retrieve existing HPA
        autoscaling_api = client.AutoscalingV1Api()
        try:
            hpa = autoscaling_api.read_namespaced_horizontal_pod_autoscaler(name=hpa_name, namespace="default")
        except client.rest.ApiException as e:
            if e.status == 404:
                print(f"HPA '{hpa_name}' not found.")
                return
            else:
                raise

        # Update max replicas
        hpa.spec.max_replicas = new_max_replicas
        hpa.spec.min_replicas = new_min_replica

        # Apply the changes
        autoscaling_api.replace_namespaced_horizontal_pod_autoscaler(name=hpa_name, namespace="default", body=hpa)
        print(f"Max replicas for HPA '{hpa_name}' updated successfully to {new_max_replicas}.")



    
    def create_service(self):
        config.load_kube_config()
        existing_service = self.get_existing_service()
        if existing_service:
            print(f"Service '{self.function_name}' already exists.")
            return
        else:
        # Define the Service object
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=self.function_name),
                spec=client.V1ServiceSpec(
                    selector={"app": self.function_name},
                    ports=[client.V1ServicePort(protocol="TCP", port=8080, target_port=8080)],
                    type="NodePort"
                )
            )

            # Create the Service
            api_instance = client.CoreV1Api()
            api_instance.create_namespaced_service(namespace="default", body=service)
            print("Service created successfully.")
            node_port = self.get_node_port()
            # global function_service_mapping
            ip = random.choice(host_ips)

            url = "http://"+ip+":"+str(node_port)+"/"+self.fname
            # function_service_mapping[self.fname] = url
            self.saveMapping("function_service_mapping.json",function_service_mapping,self.fname,url)

            return node_port
        
    def delete_service(self, service_name):
        try:
            # Load Kubernetes configuration
            config.load_kube_config()

            # Create Kubernetes API client
            api_instance = client.CoreV1Api()

            # Delete the service
            api_instance.delete_namespaced_service(name=service_name, namespace="default")

            print(f"Service '{service_name}' deleted successfully.")
        except ApiException as e:
            print(f"Exception when calling CoreV1Api->delete_namespaced_service: {e}")
            
    
    def delete_hpa(self,hpa_name):
        try:
            # Load Kubernetes configuration
            config.load_kube_config()

            # Create Kubernetes API client
            autoscaling_api = client.AutoscalingV1Api()


            # Delete the service
            autoscaling_api.delete_namespaced_horizontal_pod_autoscaler(name=hpa_name, namespace="default")

            print(f"HPA '{hpa_name}' deleted successfully.")
        except ApiException as e:
            print(f"Exception when calling CoreV1Api->delete_namespaced_service: {e}")
           
        


    def get_node_port(self):
        # Get the Service
        api_instance = client.CoreV1Api()
        service = api_instance.read_namespaced_service(name=self.function_name, namespace="default")
        
        # Extract and return the NodePort
        node_port = None
        for port in service.spec.ports:
            if port.node_port:
                node_port = port.node_port
                break
        return node_port
    
    
    def saveMapping(self,filename,mapping_data,key,value):
        #        # Load the existing JSON data from the file
        with open(filename, "r") as json_file:
            mapping_data = json.load(json_file)

        # Update the mapping data with the new key-value pair
        mapping_data[key] = value

        # Write the updated mapping data back to the file
        with open(filename, "w") as json_file:
            json.dump(mapping_data, json_file, indent=4)

        print(f"Added key-value pair '{key}': '{value}' to the mapping file:", filename)
