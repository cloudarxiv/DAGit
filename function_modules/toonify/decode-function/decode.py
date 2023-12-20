#!/usr/bin/env python3
import os
import redis
import pickle
import subprocess
import time
import logging
import json
import sys
import ffmpeg
import boto3
import requests
import shutil
from botocore.exceptions import ClientError


from urllib.request import urlopen,urlretrieve

logging.basicConfig(level=logging.INFO)

def download_video(url, file_name):
    # Download the file
    with requests.get(url, stream=True) as r:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def main():
    images_dir = "decoded-images"
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    r.flushdb() #flush previous content if any
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    
    #dwn_link = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4'
    params = json.loads(sys.argv[1])
    dwn_link = params["filename"]
    # Set how many spots you want to extract a video from. 
    parts = params["parts"]
    file_name = 'decode_video.mp4'
    download_video(dwn_link, file_name) 
    # urlretrieve(dwn_link, file_name)
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)
    probe = ffmpeg.probe(file_name)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    time1 = float(probe['streams'][0]['duration']) // 2
    width = int(video_stream['width'])
        


    intervals = time1 // parts
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
        ######################### Redis ###############################
        start1 = time.time()
        img = open(images_dir+'/Image' + str(i) + '.jpg',"rb").read()
        pickled_object = pickle.dumps(img)
        decode_output = "decode-output-image"+activation_id+"-"+str(i)
        r.set(decode_output,pickled_object)
        end1 = time.time()
        diff1 = end1 - start1
        result.append('Image'+str(i)+'.jpg')
        i += 1
        ###############################################################
    
        

    # ################################  S3 ###############################     
    start = time.time()
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=aws_region)

    
    bucket_name = 'dagit-store'
    folder_path = images_dir
    folder_name = images_dir
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(subdir, file)
            s3.upload_file(file_path, bucket_name, f'{folder_name}/{file_path.split("/")[-1]}')
            s3.put_object_acl(Bucket=bucket_name, Key=f'{folder_name}/{file_path.split("/")[-1]}', ACL='public-read')
    url_list=[]
    for image in result:
        url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
        url_list.append(url)
    
    end = time.time()
    
    diff = end - start
    
    #################################################################################################################


    try:
        image_height = int(params["height"])
        image_width = int(params["width"])
            
        print(json.dumps({"image_url_links":result,
                            "activation_id": str(activation_id),
                            "parts": parts,
                            "height": image_height,
                            "width": image_width,
                            "file_link":dwn_link
                        }))

        return({"image_url_links":result,
                "activation_id": str(activation_id),
                "parts": parts,
                "height": image_height,
                "width": image_width,
                "file_link":dwn_link
            })
    except Exception as e:
        print(json.dumps({"image_url_links":result,
                        "activation_id": str(activation_id),
                        "parts": parts,
                        "file_link":dwn_link,
                        "s3_time": diff*1000,
                        "redis_time": diff1*1000
                        }))

        return({"image_url_links":result,
                "activation_id": str(activation_id),
                "parts": parts,
                "file_link":dwn_link,
                "s3_time": diff*1000,
                "redis_time": diff1*1000
                
            })

    
if __name__ == "__main__":
    main()