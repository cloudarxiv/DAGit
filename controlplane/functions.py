import pymongo 
import json

class Functions:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["function_store"]
        self.collection = self.db["functions"]

    def register_function(self, filename, function_name, docker_image,type="cpu"):
        
        # Check if function_name already exists in the collection
        if self.collection.find_one({"function_name": function_name}):
            print(f"Function '{function_name}' already exists.")
            return function_name

        # Read the content of the script file
        with open(filename, 'r') as file:
            script_content = file.read()

        # Create a document to store in MongoDB
        document = {
            "function_name": function_name,
            "script_name": filename,
            "type": type,
            "script_content": script_content,
            "docker_image": docker_image
        }

        # Insert the document into MongoDB
        self.collection.insert_one(document)
        print(f"Function '{function_name}' succesfully registered on DAGit.")
        return function_name
        
    def list_functions(self):
        cursor = self.collection.find({}, {"_id": 0, "function_name": 1, "docker_image": 1, "type":1})
        response_data = []
        for doc in cursor:
            response_data.append({"function_name": doc["function_name"], "docker_image": doc["docker_image"], "type": doc["type"]})            
        # response_data = [{"function_name": doc["function_name"], "docker_image": doc["docker_image"]} for doc in cursor]
        response = json.dumps(response_data)
        return response
    
    def get_function(self,function_name):
        cursor = self.collection.find({"function_name":function_name}, {"_id": 0, "function_name": 1, "docker_image": 1,"script_name":1, "script_content":1,"type":1 })
        response_data = [{"function_name": doc["function_name"], "script_name": doc["script_name"], "script_content": doc["script_content"],
                          "docker_image": doc["docker_image"],"type":doc["type"]} for doc in cursor]
        response = json.dumps(response_data[0])
        return response
    
    
    def delete_function(self, function_name):
        # Delete the document corresponding to the given function name
        result = self.collection.delete_one({"function_name": function_name})
        if result.deleted_count == 1:
            print(f"Function '{function_name}' deleted successfully.")
            return True
        else:
            print(f"Function '{function_name}' not found.")
            return False
