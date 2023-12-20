
import requests
import sys
import json
import time 

def server():
    start = time.time()

    url = "http://10.129.28.219:5001/register/trigger/"
    input_json_file = open(sys.argv[1])
    params = json.load(input_json_file)
    reply = requests.post(url = url,json = params,verify=False)
    
    end = time.time()
    
    print("Response time: ", end-start)


    print(reply.json())
   

def main():
    server()

if __name__=="__main__":
    main()



