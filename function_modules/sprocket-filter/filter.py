#!/usr/bin/env python3
import os
import time
from io import BytesIO
import redis
import pickle
import subprocess
import json
import sys
import ffmpeg
from PIL import Image
import pysftp
import pilgram
import logging
from urllib.request import urlopen,urlretrieve

logging.basicConfig(level=logging.INFO)

def main():
    import time as time1
    start = time1.time()
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:

        sftp = pysftp.Connection(
            host="10.129.28.219", 
            username="faasapp",
            password="1234",
            cnopts=cnopts
        )
        logging.info("connection established successfully")
    except:
        logging.info('failed to establish connection to targeted server')

    filtered_dir = "filtered-images"
    is_images_dir = os.path.isdir(filtered_dir)
    if(is_images_dir == False):
        os.mkdir(filtered_dir)
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    
    decode_activation_id = params["activation_id"]

    decode_execution_time = params["exec_time_decode"]
    parts = params["parts"]
    filtered_result = []
    for i in range(0,parts):

        ###############################################################
        #               Fetching from redis                           #
        ###############################################################
        decode_output = "decode-output-image"+decode_activation_id+"-"+str(i)
        load_image = pickle.loads(r.get(decode_output)) #loads the data from redis
        im = Image.open(BytesIO(load_image))
        filterimg =  filtered_dir+'/filtered-Image' + str(i) + '.jpg'
        pilgram.lofi(im).save(filterimg)

        ###############################################################
        #               Storing into redis                            #
        ###############################################################
        filtered_image = open(filtered_dir+'/filtered-Image' + str(i) + '.jpg',"rb").read()
        pickled_object = pickle.dumps(filtered_image)
        filter_output = "filter-output-image"+activation_id+"-"+str(i)
        r.set(filter_output,pickled_object)
        #print("Filter output",pickle.loads(r.get(filter_output)))
        filtered_result.append(filterimg)
    
    current_path = os.getcwd()
    current_files = os.listdir(current_path+"/"+filtered_dir)
    # print("Current Files",current_files)
        
    ### Pushing filtered images to remote faasapp server using sftp
    remote_path = "/home/faasapp/Desktop/anubhav/sprocket-filter/"+filtered_dir
    try:
        sftp.chdir(remote_path)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_path)  # Create remote_path
        sftp.chdir(remote_path)
    
    #current_path = os.getcwd()
    sftp.put_d(current_path+"/"+filtered_dir,preserve_mtime=True,remotepath=remote_path)
    end = time1.time()

    exec_time = end-start
    print(json.dumps({ "filter_output": filtered_result,
                        "activation_id": str(activation_id),
                        "parts": parts,
                        "exec_time_filter": exec_time,
                        "exec_time_decode": decode_execution_time
                        }))
    

if __name__ == "__main__":
    main()