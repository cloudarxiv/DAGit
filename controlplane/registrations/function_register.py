
import requests
import sys
import json
def server():
    
    url = "http://10.129.28.219:5001/register/function/image-blur"
    files = [
    ('pythonfile', open(sys.argv[1],'rb')),
    ('dockerfile', open(sys.argv[2],'rb')),
    ('requirements.txt', open(sys.argv[3],'rb'))
    ]
    reply = requests.post(url = url,files = files,verify=False)
    print(reply.json())
   
def main():
    server()

if __name__=="__main__":
    main()

