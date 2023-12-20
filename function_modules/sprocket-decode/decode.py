#!/usr/bin/env python3
import os
import time
import redis
import pickle
from shutil import which
import subprocess
import logging
import json
import sys
import ffmpeg
import pysftp

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

    images_dir = "images"
    try:
        remoteArtifactPath="/home/faasapp/Desktop/anubhav/sprocket-decode/"+images_dir

        filesInRemoteArtifacts = sftp.listdir(path=remoteArtifactPath)
        for file in filesInRemoteArtifacts:
            sftp.remove(remoteArtifactPath+file)
    except:
        
        is_images_dir = os.path.isdir(images_dir)
        if(is_images_dir == False):
            os.mkdir(images_dir)

    
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    r.flushdb() #flush previous content if any
    
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    
    #dwn_link = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4'
    params = json.loads(sys.argv[1])
    dwn_link = params["filename"]
    
    # Set how many spots you want to extract a video from. 
    parts = params["parts"]
    file_name = 'decode_video.mp4' 
    
    urlretrieve(dwn_link, file_name)
    sftp.put(file_name,preserve_mtime=True,remotepath="/home/faasapp/Desktop/anubhav/sprocket-decode/input.mp4")

    
   
    probe = ffmpeg.probe(file_name)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    time = float(probe['streams'][0]['duration']) // 2
    width = int(video_stream['width'])
    #width = probe['streams'][0]['width']
    


    intervals = time // parts
    intervals = int(intervals)
    interval_list = [(i * intervals, (i + 1) * intervals) for i in range(parts)]
    
    result = []

    for i in range(0,parts):
        if os.path.exists(images_dir+'/Image' + str(i) + '.jpg'):
            os.remove(images_dir+'/Image' + str(i) + '.jpg')

    i = 0
    for item in interval_list:
        out = (
            ffmpeg
            .input(file_name, ss=item[1])
            .filter('scale', width, -1)
            .output(images_dir+'/Image' + str(i) + '.jpg', vframes=1)
            .run(capture_stdout=False)
            
        )
        
        img = open(images_dir+'/Image' + str(i) + '.jpg',"rb").read()
        
        pickled_object = pickle.dumps(img)
        decode_output = "decode-output-image"+activation_id+"-"+str(i)
        r.set(decode_output,pickled_object)
        
        result.append('Image'+str(i)+'.jpg')
        



        i += 1
    remote_path = "/home/faasapp/Desktop/anubhav/sprocket-decode/"+images_dir
    try:
        sftp.chdir(remote_path)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_path)  # Create remote_path
        sftp.chdir(remote_path)
    
    current_path = os.getcwd()
    sftp.put_d(current_path+"/"+images_dir,preserve_mtime=True,remotepath=remote_path)

    end = time1.time()

    exec_time = end-start
    
    print(json.dumps({"decode_output":result,
                        "activation_id": str(activation_id),
                        "parts": parts,
                        "file_link":dwn_link,
                        "exec_time_decode":exec_time
                        }))
    
if __name__ == "__main__":
    main()