
import subprocess
import shutil
import threading
import json
import os
import io

from flask import Flask, request,jsonify
import pymongo
import orchestrator
import validate_trigger
import redis_setup
import minio_dagit
import time
import logging
from datetime import datetime
from queue import Queue
import multiprocessing


from functions import Functions
from deployment import DeploymentManager

import cProfile
import pstats




app = Flask(__name__)

bucket_name = 'dagit-store'


# create minio client 
minio_client = minio_dagit.create_minio_client(bucket_name)    

### Create in-memory redis storage ###
redis_instance = redis_setup.create_redis_master_instance()
# redis_slave = redis_setup.create_redis_slave_instance()



# configure logging
# logging.basicConfig(filename='dagit_request_logs.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the logger
logging.basicConfig(filename='dagit_request_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)


action_url_mappings = {} #Store action->url mappings
action_properties_mapping = {} #Stores the action name and its corresponding properties
responses = []
list_of_func_ids = [] 

trigger_cache = {}

@app.route("/")
def home():
    data = {"message": "Hello, Welcome to DAGit","author":"Anubhav Jana"}
    return jsonify(data)

@app.route('/view/functions', methods=['GET'])
def list_actions():
    list_of_actions = []
    stream = os.popen(' wsk -i action list')
    actions = stream.read().strip().split(' ')
    try:
        for action in actions:
            if action=='' or action=='private' or action=='blackbox':
                continue
            else:
                list_of_actions.append(action.split('/')[2])
        data = {"status": 200,"DAGit functions":list_of_actions}
        return data
    except Exception as e:
        data = {"status": 404, "failure reason": e}

@app.route('/register/trigger/',methods=['POST'])
def register_trigger():
    trigger_json = request.json
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["trigger_store"]
    mycol = mydb["triggers"]
    try:
        cursor = mycol.insert_one(trigger_json)
        print("TRIGGER REGISTERED: ",cursor.inserted_id)
        if(trigger_json["type"]=="dag"):
            targets = trigger_json["dags"]
        elif(trigger_json["type"]=="function"):
            targets = trigger_json["functions"]
        data = {"status":"success","trigger_name":trigger_json["trigger_name"],"trigger_type":trigger_json["type"],"trigger_target":targets}
        return json.dumps(data)
    except Exception as e:
        data = {"status":"fail","reason":e}
        return json.dumps(data)


@app.route('/register/function/<function_name>',methods=['POST'])
def register_function(function_name):
    list_of_file_keys = []
    document = {}
    function_dir = '/home/faasapp/Desktop/anubhav/function_modules' # Library of functions
    new_dir = function_name
    destination = os.path.join(function_dir, new_dir)
    # Create the directory
    os.makedirs(destination, exist_ok=True)
    files = request.files
    for filekey in files:
        if filekey!='description':
            list_of_file_keys.append(filekey)
    for key in list_of_file_keys:
        file = request.files[key]
        filename = file.filename
        # Save, copy, remove
        file.save(file.filename)
        shutil.copy(filename, destination)
        os.remove(filename)
    image_build_script = 'buildAndPush.sh'
    shutil.copy(image_build_script, destination)
    
    # Prepare data 
    document["function_name"] = function_name
    document["image_build_script"] = 'buildAndPush.sh'
    document["python_script"] = (request.files[list_of_file_keys[0]]).filename
    document["dockerfile"] = (request.files[list_of_file_keys[1]]).filename
    document["requirements.txt"] =(request.files[list_of_file_keys[2]]).filename

    docker_image_name = "10.129.28.219:5000/"+function_name+"-image"
    api_name = "/"+function_name+"-api"
    path_name = "/"+function_name+"-path"
    password = '1234'
    # build docker image
    cmd = ["sudo", "-S", "/home/faasapp/Desktop/anubhav/controlplane/build_image.sh",destination,docker_image_name]
    # open subprocess with Popen
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # pass password to standard input
    process.stdin.write(password + "\n")
    process.stdin.flush()

    # wait for process to complete and get output
    output, errors = process.communicate()
    print("OUTPUT---------",output)
    print("ERRORS---------",errors)
    # if(errors):
    #     print("There is error building docker file")
    #     data = {"message":"fail","reason":"docker build failed"}
    #     return json.dumps(data)
    # else:

        # create action, register action with api, populate its mapping
    subprocess.call(['./create_action.sh',destination,docker_image_name,function_name])
    subprocess.call(['./register.sh',api_name,path_name,function_name])
    subprocess.call(['bash', './actions.sh'])
    
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["function_store"]
    mycol = mydb["functions"]
    try:
        cursor = mycol.insert_one(document)
        print("OBJECT ID GENERATED",cursor.inserted_id)
        data = {"message":"success"}
        return json.dumps(data)
    except Exception as e:
        print("Error--->",e)
        data = {"message":"fail","reason":e}
        return json.dumps(data)

        # data = {"message":"success"}
        # return json.dumps(data)


@app.route('/register/dag/',methods=['POST'])
def register_dag():
    dag_json = request.json
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["dag_store"]
    mycol = mydb["dags"]
    try:
        cursor = mycol.insert_one(dag_json)
        print("DAG registered: ",cursor.inserted_id)
        data = {"message":"success"}
        return json.dumps(data)
    except Exception as e:
        print("Error registering DAG--->",e)
        data = {"message":"fail","reason":e}
        return json.dumps(data)

@app.route('/view/dag/<dag_name>',methods=['GET'])
def view_dag(dag_name):
    dag_info_map = {}
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["dag_store"]
    mycol = mydb["dags"]
    document = mycol.find({"name":dag_name})
    data = list(document)
    dag_info_list = []
    for items in data:
        dag_info_list = items["dag"]
        dag_info_map["dag_name"] = items["name"]
    
    dag_info_map["number_of_nodes"] = len(dag_info_list)
    dag_info_map["starting_node"] = dag_info_list[0]["node_id"]

    for dag_items in dag_info_list:
        node_info_map = {}
        if(len(dag_items["properties"]["outputs_from"])==0):
            node_info_map["get_outputs_from"] = "Starting action - >No outputs consumed"
        else:
            node_info_map["get_outputs_from"] = dag_items["properties"]["outputs_from"]
        node_info_map["primitive"] = dag_items["properties"]["primitive"]
        if(dag_items["properties"]["primitive"]=="condition"):
            node_info_map["next_node_id_if_condition_true"] = dag_items["properties"]["branch_1"]
            node_info_map["next_node_id_if_condition_false"] = dag_items["properties"]["branch_2"]
        else:
            if(dag_items["properties"]["next"]!=""):
                node_info_map["next_function"] = dag_items["properties"]["next"]
            else:
                node_info_map["next_function"] = "Ending node_id of a path"
        dag_info_map[dag_items["node_id"]] = node_info_map
    response = {"dag_data":dag_info_map}
    # formatted_json = json.dumps(response, indent=20)
    return response

@app.route('/view/dags',methods=['GET'])
def view_dags():
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["dag_store"]
    mycol = mydb["dags"]
    document = mycol.find()
    data = list(document)
    # Serialize the data to JSON
    json_data = json.dumps(data, default=str)
    json_string ='{"dag":'+str(json_data)+'}'
    data = json.loads(json_string)
    # # Format the JSON string with indentation
    # formatted_json = json.dumps(data, indent=4)
    return data

@app.route('/view/triggers',methods=['GET'])
def view_triggers():
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["trigger_store"]
    mycol = mydb["triggers"]
    document = mycol.find()
    data = list(document)
    # Serialize the data to JSON
    json_data = json.dumps(data, default=str)
    json_string ='{"trigger":'+str(json_data)+'}'
    data = json.loads(json_string)
    # Format the JSON string with indentation
    # formatted_json = json.dumps(data, indent=4)
    return data

@app.route('/view/trigger/<trigger_name>',methods=['GET'])
def view_trigger(trigger_name):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
    mydb = myclient["trigger_store"]
    mycol = mydb["triggers"]
    query = {"trigger_name":trigger_name}
    projection = {"_id": 0,"trigger_name":1,"type":1,"trigger":1,"dags":1,"functions":1}
    document = mycol.find(query,projection)
    data = list(document)
    # print(data)
    json_data = json.dumps(data, default=str)
    json_string ='{"trigger":'+str(json_data)+'}'
    data = json.loads(json_string)
    formatted_json = json.dumps(data, indent=4)
    return formatted_json
    
# EXAMPLE URL: http://10.129.28.219:5001/view/activation/8d7df93e8f2940b8bdf93e8f2910b80f
@app.route('/view/activation/<activation_id>', methods=['GET', 'POST'])
def list_activations(activation_id):
    # activation_id = '74a7b6c707d14973a7b6c707d1a97392'
    cmd = ['wsk', '-i', 'activation', 'get', activation_id]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    json_res = result.stdout.decode().split('\n')[1:] # Ignore first line of output
    res = json.loads('\n'.join(json_res))
    d={}
    d["action_name"] = res["name"]
    d["duration"] = res["duration"]
    d["status"] = res["response"]["status"]
    d["result"] = res["response"]["result"]
    return({"action_name":res["name"],
            "duration": res["duration"],
            "status": res["response"]["status"],
            "result":res["response"]["result"]
        })

# EXAMPLE URL: http://10.129.28.219:5001/view/dag/76cc8a53-0a63-47bb-a5b5-9e6744f67c61
@app.route('/view/<dag_id>',methods=['GET'])
def view_dag_metadata(dag_id):
    try:
        myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
        mydb = myclient["dag_store"]
        mycol = mydb["dag_metadata"]
        query = {"dag_activation_id":dag_id}
        projection = {"_id": 0,
                      "dag_activation_id":1,
                      "id":1,
                      "start_timestamp":1,
                      "end_timestamp":1,
                      "time_first_deque_timestamp":1,
                      "dag_execution_time_in_secs":1,
                      "total_bytes_written":1,
                      "functions":1,
                      "total_bytes_read":1}
        document = mycol.find(query, projection)
        data = list(document)
        response = {"dag_metadata":data}
        return json.dumps(response)
    except Exception as e:
        response = {"error":e}
        return json.dumps(response)
    
@app.route('/view/function/<function_id>',methods=['GET'])
def view_function_metadata(function_id):
    try:
        myclient = pymongo.MongoClient("mongodb://127.0.0.1/27017")
        mydb = myclient["dag_store"]
        mycol = mydb["function_metadata"]
        
        query = {f"{function_id}.function_activation_id": function_id}
        
        projection = {"_id": 0,
                      f"{function_id}.function_id": 1,
                      f"{function_id}.function_activation_id": 1,
                      f"{function_id}.function_start_timestamp": 1,
                      f"{function_id}.function_end_timestamp": 1,
                      f"{function_id}.function_output": 1,
                      f"{function_id}.byes_written": 1,
                      f"{function_id}.bytes_read": 1,
                      f"{function_id}.node_name": 1
                    }
        document = mycol.find(query, projection)
        data = list(document)        
        response = {"function_metadata": data}
        return json.dumps(response,indent=4)
    except Exception as e:
        response = {"error": str(e)}
        return json.dumps(response)



@app.route('/delete/dag/<dag_id>',methods=['DELETE'])
def delete_dag_metadata(dag_id):
    # Establish connection to MongoDB
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["dag_store"]
    mycol = mydb["dag_metadata"]
    query = {"dag_activation_id": dag_id}
    # Perform the delete operation
    result = mycol.delete_one(query)

    if result.deleted_count == 1:
        response = {"message":"success"}
        return json.dumps(response)
    else:
        response = {"message":"failed"}
        return json.dumps(response)
    

app.route('/delete/function/<function_id>',methods=['DELETE'])
def delete_dag_metadata(function_id):
    # Establish connection to MongoDB
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["dag_store"]
    mycol = mydb["function_metadata"]
    query = {"function_activation_id": function_id}
    # Perform the delete operation
    result = mycol.delete_one(query)

    if result.deleted_count == 1:
        response = {"message":"success"}
        return json.dumps(response)
    else:
        response = {"message":"failed"}
        return json.dumps(response)
    


# EXAMPLE URL: http://10.129.28.219:5001/run/action/odd-even-action
# http://10.129.28.219:5001/run/action/decode-function

def execute_action(action_name):
    try:
        res = orchestrator.execute_action(action_name)
        data = {"status": 200,"dag_output":res}
        return data
    except Exception as e:
        data = {"status": 404 ,"failure_reason":e}
        return data

# Define a function to execute orchestrator.execute_dag in a thread
def execute_dag_in_thread(dag_details, request_json, minio_client, redis_instance, bucket_name, result_queue):
    thread_id = threading.get_ident()
    # pr = cProfile.Profile()

    try:       
            
        request_start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        # pr.enable()
        res, workflow_start_timestamp, workflow_end_timestamp, workflow_duration, dag_id, dag_name = orchestrator.execute_dag(dag_details, request_json, minio_client, redis_instance, bucket_name,thread_id)
        # pr.disable()
        request_end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        request_duration = (datetime.strptime(request_end_timestamp, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(request_start_timestamp, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()      
       

        if res:
            logging.info("{}, {}, {},{}, {}, {}, {}, {}".format(request_start_timestamp, request_end_timestamp, workflow_start_timestamp, workflow_end_timestamp, request_duration, workflow_duration, dag_name, dag_id))
            result_queue.put({
                "response": res,
                "status": 200,
                "request_start_timestamp": request_start_timestamp,
                "request_end_timestamp": request_end_timestamp,
                "request_duration_seconds": request_duration,
                "workflow_duration_seconds": workflow_duration,
                "workflow_start_timestamp": workflow_start_timestamp,
                "workflow_end_timestamp": workflow_end_timestamp,
                "dag_activation_id": dag_id,
                "dag_id": dag_name
            })
        else:
            result_queue.put({"response": "Workflow did not execute completely", "status": 400})
    except Exception as e:
        result_queue.put({"response": "failed", "status": 400, "reason":str(e)})


   
# EXAMPLE URL: http://10.129.28.219:5001/run/mydagtrigger
@app.route('/run/<trigger_name>', methods=['GET', 'POST'])
def orchestrate_dag(trigger_name):   
    
    global trigger_cache
    orchestrator.dag_responses = []
    try:
        # Check if the trigger is already cached
        if trigger_name in trigger_cache:            
            triggers = trigger_cache[trigger_name]
        else:
           
            # If not cached, fetch and validate the trigger
            triggers = validate_trigger.get_trigger_json(trigger_name)            
            trigger_cache[trigger_name] = triggers
        
        if len(triggers) == 0:
            return {"response": "the given trigger is not registered in DAGit trigger store"}
        else:
            thread_list = []
            if triggers[0]['type'] == 'dag':
                # dags = triggers[0]['dags']
                
                try:                   
                    
                    
                    try:
                        request_start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]            

                        res, workflow_start_timestamp, workflow_end_timestamp, workflow_duration, dag_id, dag_name = orchestrator.execute_dag(triggers[0]['dags'][0], request.json, redis_instance,minio_client,bucket_name)
                        request_end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  
                        
                        request_duration = (datetime.strptime(request_end_timestamp, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(request_start_timestamp, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
                                        
                        workflow_duration =  (datetime.strptime(workflow_end_timestamp, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(workflow_start_timestamp, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()

                       logging.info("{}, {}, {},{}, {}, {}, {}, {}".format(request_start_timestamp,request_end_timestamp,workflow_start_timestamp,workflow_end_timestamp,request_duration,workflow_duration,dag_name,dag_id))

                        return jsonify({"response": res, "status": 200, 
                                "request_start_timestamp":request_start_timestamp,
                                "request_end_timestamp": request_end_timestamp,
                                "request_duration_seconds": request_duration,
                                "workflow_duration_seconds": workflow_duration,
                                "workflow_start_timestamp":workflow_start_timestamp,
                                "workflow_end_timestamp": workflow_end_timestamp,
                                "dag_activation_id":dag_id,
                                "dag_id": dag_name
                                })                     
                       
                        
                    except Exception as e:
                        print("------Error line 519---", str(e)) 
                        return{"response":"Workflow did not execute completely", "status": 400}                   
                   

                except Exception as e:
                    print("Error------->",e)
                    return {"response": "failed", "status": 400, "reason": str(e)}

            else:
                try:
                    functions = triggers[0]['functions']
                    arguments = request.json
                    # with lock:
                    for function in functions:
                        thread_list.append(threading.Thread(target=orchestrator.execute_action, args=[function, arguments]))
                    for thread in thread_list:
                        thread.start()
                    for thread in thread_list:
                        thread.join()

                    return {"response": orchestrator.function_responses, "status": 200}
                except Exception as e:
                    return {"response": "failed", "status": 400}

    except Exception as e:
        data = {"status": 404, "message": "failed"}
        return data


if __name__ == '__main__':
    # Number of processes you want to run concurrently
    num_processes = 5
    
    # Port number for the first process
    base_port = 5001
    
    # Create a list to store the processes
    processes = []
    
    # Start multiple processes with different port numbers
    for i in range(num_processes):
        port = base_port + i
        p = multiprocessing.Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': port})
        p.start()
