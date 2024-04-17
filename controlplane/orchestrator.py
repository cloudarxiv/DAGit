#!/usr/bin/env python3

import sys
import requests
import uuid
import re
import datetime
import subprocess
import threading
import queue
import redis
import pickle
import json
import os
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import pymongo
import asyncio
import multiprocessing
from datetime import datetime


# max_concurrent_requests = 400  # Adjust as needed
# queue_semaphore = threading.Semaphore(value=max_concurrent_requests)


queue_lock = threading.Lock()


from concurrent.futures import ThreadPoolExecutor


url_cache = {}

dag_cache = {}


# import redis_setup
import minio_dagit

import time


import logging

# Configure the logging settings
# logging.basicConfig(filename='dagit.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



action_url_mappings = {} #Store action->url mappings
action_properties_mapping = {} #Stores the action name and its corresponding properties
responses = []
queue = []
list_of_func_ids = []
function_ids = {}
function_responses = []
dag_responses = []

functions = {} # to store function name -> function id mapping

function_metadata = {}

bytes_written_per_function = []


def get_scheduling_decision(substring,dag_index,dag_id,function,function_id):
    # Run kubectl command to get pod names containing the specified substring
    pod_names_command = f'kubectl get pod | grep {substring} | awk "{{print $1}}"'
    pod_names_process = subprocess.run(pod_names_command, shell=True, capture_output=True, text=True)

    if pod_names_process.returncode != 0:
        logging.error("Error retrieving pod names: {}".format(pod_names_process.stderr))
        # print(f"Error retrieving pod names: {pod_names_process.stderr}")
        return None

    # Extract pod names and get node names
    pod_names = pod_names_process.stdout.strip().split('\n')
    # scheduling_decisions = []

    for pod_name in pod_names:
        # print("-----------Line 53------", pod_name)
        # Remove additional details from the pod name
        pod_name = pod_name.split()[0]

        get_node_command = ['kubectl', 'get', 'pod', pod_name, '-o', 'jsonpath={.spec.nodeName}']
        get_node_process = subprocess.run(get_node_command, capture_output=True, text=True)

        if get_node_process.returncode != 0:
            logging.error("Error retrieving node name for pod {}: {}".format(pod_name,get_node_process.stderr))
            # print(f"Error retrieving node name for pod {pod_name}: {get_node_process.stderr}")
        else:
            node_name = get_node_process.stdout.strip()
            decision = (dag_index, dag_id, function, function_id, node_name)
            # scheduling_decisions.append(decision)
            
    return node_name,decision


            
            # print(f"Pod {pod_name} is running on node {node_name}")
        


def preprocess(filename):
    with open(filename) as f:
        lines = f.readlines()
    action_url_list = []
    for line in lines:
        line = line.replace("\n", "")
        line = line.replace("/guest/","")
        action_url_list.append(line)
    for item in action_url_list:
        action_name = item.split(' ')[0]
        url = item.split(' ')[1]
        action_url_mappings[action_name] = url


# def execute_thread(action,redis,url,json):
#     reply = requests.post(url = url,json=json,verify=False)
#     list_of_func_ids.append(reply.json()["activation_id"])
#     logging.info("Function {} completed execution || Function ID : {}".format(action,reply.json()["activation_id"]))
#     redis.set(action+"-output",pickle.dumps(reply.json()))
#     responses.append(reply.json())

def execute_thread(action, redis, url, json):
    try:
        function_start_timestamp = time.time()
        reply = requests.post(url=url, json=json, verify=False)
        reply.raise_for_status()
        
        # Check if the response has content and is valid JSON
        if reply.text:
            function_end_timestamp = time.time()
            # time_to_complete = time_end - time_start
            list_of_func_ids.append(reply.json()["activation_id"])
            function_id = reply.json()["activation_id"]
            # function_ids[reply.json()["activation_id"]] = time_to_complete
            functions[action] = function_id            
            logging.info("Function {} completed execution || Function ID : {}".format(action, reply.json()["activation_id"]))

            # Your existing code to store the response in Redis
            redis.set(action + "-output", pickle.dumps(reply.json()))
            
            memory_usage = redis.memory_usage(action + "-output")
            bytes_written_per_function.append(memory_usage)

            responses.append(reply.json())
            # Record metadata for the function ID
            function_metadata[function_id] = {"function_id": action, 
                                                  "function_activation_id":function_id,
                                                  "function_start_timestamp": function_start_timestamp,
                                                  "function_end_timestamp": function_end_timestamp,
                                                  "function_output": reply.json(),
                                                  "byes_written":0,
                                                  "bytes_read": memory_usage}    
            
            
        else:
            logging.warning("Empty or invalid JSON response for function {}".format(action))

    except requests.exceptions.RequestException as e:
        logging.error(f"Error executing function {action}: {str(e)}")

    

def handle_parallel(queue,redis,action_properties_mapping,parallel_action_list):
    # print("going into parallel ---- line 98")
    responses.clear() # clear response so that no 
    thread_list = []
    output_list = [] # List to store the output of actions whose outputs are required by downstream operations
    
    for action in parallel_action_list:
        action_names = action_properties_mapping[action]["outputs_from"]        
        next_action = action_properties_mapping[action]["next"]
        if(next_action!=""):
            if next_action not in queue:
                queue.append(next_action)
        if(len(action_names)==1): # if only output of one action is required
            key = action_names[0]+"-output"
            output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
            action_properties_mapping[next_action]["arguments"] = output 
            # output = pickle.loads(redis.get(key))
            # action_properties_mapping[action]["arguments"] = output
            # print("----- Line 113--------",output)
        else:
            list_of_keys = []
            for item in action_names:
                key = item+"-output"
                list_of_keys.append(key)                                    
            output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
            action_properties_mapping[next_action]["arguments"] = output
            # for item in action_names:
            #     key = item+"-output"
            #     output = pickle.loads(redis.get(key))
            #     output_list.append(output)           
            
            # action_properties_mapping[action]["arguments"] = output_list
        
        # url = action_url_mappings[action]
        url = get_url(action)
        # print("---------------------------url----------------------------",url)
        thread_list.append(threading.Thread(target=execute_thread, args=[action,redis,url,action_properties_mapping[action]["arguments"]]))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    action_properties_mapping[next_action]["arguments"] = responses
    return responses

def get_dag_json(dag_name):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["dag_store"]
    mycol = mydb["dags"]
    query = {"name":dag_name}
    projection = {"_id": 0, "name": 1,"dag":1}
    document = mycol.find(query, projection)
    data = list(document)
    return data

def submit_dag_metadata(dag_metadata):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["dag_store"]
    mycol = mydb["dag_metadata"]
    try:
        cursor = mycol.insert_one(dag_metadata)
        data = {"message":"success"}
        dag_metadata.clear()
        # print(data)
        return json.dumps(data)
    except Exception as err:
        data = {"message":"failed","reason":err}
        # print(data)
        return json.dumps(data)
    
def submit_function_metadata(function_metadata):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["dag_store"]
    mycol = mydb["function_metadata"]
    try:
        cursor = mycol.insert_one(function_metadata)
        data = {"message":"success"}
        return json.dumps(data)
    except Exception as err:
        data = {"message":"failed","reason":err}
        return json.dumps(data)
    
    
def handle_scheduling_decision(list_of_functions,dag_name,dag_id,functions,scheduling_decisions):
    
    for action_name in list_of_functions:
        action = action_name.replace("_", "-")
        pod_substring="guest-"+action                
        # node_name,decision = get_scheduling_decision(pod_substring,dag_name,dag_id,action,reply.json()["activation_id"])
        
        node_name,decision = get_scheduling_decision(pod_substring,dag_name,dag_id,action,functions[action_name])
        
        function_metadata[functions[action_name]]["node_name"] = node_name
        
        scheduling_decisions.append(decision)   
        
        
def clear_redis(redis_instance):
    redis_instance.flushdb()  
    
def get_url(function):
    global url_cache
    
    # Check if the URL is already cached
    if function in url_cache:
        # print("Found from cache...",function)
        return url_cache[function]
    
   
    file_path = "function_service_mapping.json"
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        
    function_name = function
    if function_name in data:
        url = data[function_name]
        url_cache[function] = url # cache the url
        return url
    else:
        return ""

# function to execute only a single function
def execute_action(action_name,request):    
    # url = action_url_mappings[action_name]
    url = get_url(action_name)
    reply = requests.post(url = url,json = request,verify=False)
    function_responses.append(reply.json())
    

# Controller Function to orchestrate a DAG
def execute_dag(dag_name,request,redis_instace,minio_client,bucket_name):    
    global dag_cache
    max_retries=3
    retry_delay=5
    
    scheduling_decisions = []   
    
    list_of_functions = []
    action_properties_mapping = {} # Stores the action name and its corresponding properties
    dag_metadata={}
    function_metafdata = {}

    dag_id = str(uuid.uuid4()) # generate a workflow id 
    
    workflow_start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    # workflow_start_timestamp = time.time()   
    

    ####################################### 
    if dag_name in dag_cache:
        # print("DAG found in cache....")
        dag_data = dag_cache[dag_name]
    else:
        # print("DAG not found in cache....")
        dag_res = json.loads(json.dumps(get_dag_json(dag_name)))
        dag_data = dag_res[0]["dag"]
        dag_cache[dag_name] = dag_data
   
    for dag_item in dag_data:
        action_properties_mapping[dag_item["node_id"]] = dag_item["properties"]
        
    # scheduling_decisions = []    
    flag = 0
    for dag_item in dag_data:
        if(flag==0): # To indicate the first action in the DAG
            queue.append(dag_item["node_id"])
            list_of_functions.append(dag_item["node_id"])  
            action_properties_mapping[dag_item["node_id"]]["arguments"] = request         
        
        while(len(queue)!=0): 
                   
            action = queue.pop(0)
            action_type = action_properties_mapping[action]["primitive"]

        
           
            if(flag==0):
                time_first_deque_timestamp = time.time()
               
            flag=flag+1
            ##########################################################
            #               HANDLE THE ACTION                        #
            ##########################################################
            if isinstance(action, str):
                url = get_url(action)
                json_data = action_properties_mapping[action]["arguments"]
                # url = action_url_mappings[action]
                # logging.info("Function {} started execution".format(action))              
                
                try:
                    function_start_timestamp = time.time()
                    reply = requests.post(url=url, json=json_data,verify=False)
                    try:
                        pass                        
                    except Exception as e:
                        print("Error Line 353-------", e)
                except requests.exceptions.RequestException as e:
                    print("Error DAGit LOG: ",e)
                    
                retries = 0               

                function_end_timestamp = time.time()
                function_id = reply.json()["activation_id"]                
                                                
                list_of_func_ids.append(function_id)
                functions[action] = function_id               

                redis_instace.set(action+"-output",pickle.dumps(reply.json()))
                memory_usage = redis_instace.memory_usage(action + "-output")
                bytes_written_per_function.append(memory_usage)
                
                # Record metadata for the function ID
                function_metadata[function_id] = {"function_id": action, 
                                                  "function_activation_id":function_id,
                                                  "function_start_timestamp": function_start_timestamp,
                                                  "function_end_timestamp": function_end_timestamp,
                                                  "function_output": reply.json(),
                                                  "byes_written":0,
                                                  "bytes_read": memory_usage}
                

                
                ##############################  HANDLE CONDITION  ##############################
                
                if(action_type=="condition"):
                    branching_action = action_properties_mapping[action]["branch_1"]
                    alternate_action = action_properties_mapping[action]["branch_2"]
                    source = action_properties_mapping[action]["condition"]["source"]
                    result=reply.json()[source]
                    print(result)
                    condition_op = action_properties_mapping[action]["condition"]["operator"]
                    
                    ###########################################################################################################S
                    if(condition_op=="equals"):
                        
                        if(isinstance(action_properties_mapping[action]["condition"]["target"], str)):
                            target = int(action_properties_mapping[action]["condition"]["target"])
                        else:
                            target=action_properties_mapping[action]["condition"]["target"]

                        if(result==target):
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(branching_action)
                            action_names = action_properties_mapping[branching_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[next_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[next_action]["arguments"] = output
                            
                        else:
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(alternate_action)
                            action_names = action_properties_mapping[alternate_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[next_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[next_action]["arguments"] = output
                                
                    ####################################################################################################
                            
                    if(condition_op=="greater_than"):
                        
                        if(isinstance(action_properties_mapping[action]["condition"]["target"], str)):
                            target = int(action_properties_mapping[action]["condition"]["target"])
                        else:
                            target=action_properties_mapping[action]["condition"]["target"]

                        if(result>target):
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(branching_action)
                            action_names = action_properties_mapping[branching_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[next_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[next_action]["arguments"] = output
                            
                        else:
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(alternate_action)
                            action_names = action_properties_mapping[alternate_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[next_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[next_action]["arguments"] = output
                                
                    #############################################################################################            
                    if(condition_op=="greater_than_equals"):
                        
                        if(isinstance(action_properties_mapping[action]["condition"]["target"], str)):
                            target = int(action_properties_mapping[action]["condition"]["target"])
                        else:
                            target=action_properties_mapping[action]["condition"]["target"]

                        if(result>=target):
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(branching_action)
                            action_names = action_properties_mapping[branching_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[branching_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[branching_action]["arguments"] = output
                            
                        else:
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(alternate_action)
                            action_names = action_properties_mapping[alternate_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[alternate_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[alternate_action]["arguments"] = output
                                
                    ################################################################################################
                    if(condition_op=="less_than"):
                        
                        if(isinstance(action_properties_mapping[action]["condition"]["target"], str)):
                            target = int(action_properties_mapping[action]["condition"]["target"])
                        else:
                            target=action_properties_mapping[action]["condition"]["target"]
                            
                        print(target)

                        if(result<target):
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(branching_action)
                            action_names = action_properties_mapping[branching_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[branching_action]["arguments"] = output 
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[branching_action]["arguments"] = output
                            
                        else:
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(alternate_action)
                            action_names = action_properties_mapping[alternate_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[alternate_action]["arguments"] = output  
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[alternate_action]["arguments"] = output
                        
                    ##############################################################################################################   
                    
                    if(condition_op=="less_than_equals"):
                        if(isinstance(action_properties_mapping[action]["condition"]["target"], str)):
                            target = int(action_properties_mapping[action]["condition"]["target"])
                        else:
                            target=action_properties_mapping[action]["condition"]["target"]

                        if(result<=target):
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(branching_action)
                            action_names = action_properties_mapping[branching_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[branching_action]["arguments"] = output   
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[branching_action]["arguments"] = output
                            
                        else:
                            output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                            queue.append(alternate_action)
                            action_names = action_properties_mapping[alternate_action]["outputs_from"] # Get the list of actions whose output will be used
                            if(len(action_names)==1): # if only output of one action is required
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                action_properties_mapping[alternate_action]["arguments"] = output                               
                            else:
                                list_of_keys = []
                                for item in action_names:
                                    key = item+"-output"
                                    list_of_keys.append(key)                                    
                                output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}                                   
                                action_properties_mapping[alternate_action]["arguments"] = output
                
                # HANDLE SERIAL PRIMITIVE
                                
                elif(action_type=="serial"):                   
                    next_action = action_properties_mapping[action]["next"]
                    if(next_action!=''):
                        list_of_functions.append(next_action)
                    if(next_action!=""):
                        output_list = [] # List to store the output of actions whose outputs are required by downstream operations
                        queue.append(next_action)
                        action_names = action_properties_mapping[next_action]["outputs_from"] # Get the list of actions whose output will be used
                        if(len(action_names)==1): # if only output of one action is required
                            try:
                                key = action_names[0]+"-output"
                                output = {"key":key, "host": "10.110.12.209", "port": 6379}                               
                                # output = pickle.loads(redis_instace.get(key))
                                action_properties_mapping[next_action]["arguments"] = output
                            except Exception as e:
                                print("Error: ",e)
                        else:
                            list_of_keys = []
                            for item in action_names:
                                key = item+"-output"
                                list_of_keys.append(key)
                                
                            output = {"key":list_of_keys, "host": "10.110.12.209", "port": 6379}  
                                # output = pickle.loads(redis_instace.get(key))
                                # output_list.append(output)
                            action_properties_mapping[next_action]["arguments"] = output
                
                # HANDLE PARALLEL PRIMITIVE
                
                elif(action_type=="parallel"):
                    parallel_action_list = action_properties_mapping[action]["next"]
                    for action in parallel_action_list:
                        list_of_functions.append(action)
                    queue.append(parallel_action_list)
                    
                    
            else:
                
                reply = handle_parallel(queue,redis_instace,action_properties_mapping,action) 
    
        
    # PREPARAING WORKFLOW LEVEL METRICS
    
    dag_metadata={}
    dag_metadata["time_first_deque_timestamp"] = time_first_deque_timestamp
    dag_metadata["dag_activation_id"] = dag_id
    dag_metadata["id"] = dag_name
    dag_metadata["functions"] = functions
    dag_metadata["total_bytes_written"] = bytes_written_per_function
    dag_metadata["total_bytes_read"] = 0    
        
    
    redis_instace.flushdb()       
        
        
    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor() as executor1:      
        
        executor1.submit(submit_function_metadata, function_metadata)      
    
    
    workflow_end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    workflow_duration = (datetime.strptime(workflow_end_timestamp, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(workflow_start_timestamp, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()

    dag_metadata["start_timestamp"] = workflow_start_timestamp
    dag_metadata["end_timestamp"] = workflow_end_timestamp
    dag_metadata["dag_execution_time_in_secs"] = workflow_duration

    with ThreadPoolExecutor() as executor2:       
    
        executor2.submit(submit_dag_metadata, dag_metadata) # submit DAG metadata
        
        executor2.submit(clear_redis,redis_instace) # Flush redis 
    
        
    # submit_dag_metadata(dag_metadata)  

    
    # submit_function_metadata(function_metadata)
    
    # dag_metadata = {}
    # function_metadata = {}  
    
    # dag_metadata.clear()
    function_metadata.clear()   
    bytes_written_per_function.clear()

    
    if(isinstance(reply,list)):
        res = {"dag_activation_id": dag_id,
                "result": reply
            }
    else:
        res = { 
                "dag_activation_id": dag_id,
                "result": reply.json()
            }
    

    minio_dagit.write_to_minio(minio_client,res,dag_name+'-'+dag_id+'.json',bucket_name)  
    
    

    
    return res,workflow_start_timestamp,workflow_end_timestamp,workflow_duration,dag_id,dag_name
            
