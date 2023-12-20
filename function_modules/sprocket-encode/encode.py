#!/usr/bin/env python3
import cv2
import time
import os
import sys
import redis
import pickle
import json
import boto3
import requests


def main():
    # filtered_dir = "filtered-images"
    # is_images_dir = os.path.isdir(filtered_dir)
    # if(is_images_dir == False):
    #     os.mkdir(filtered_dir)
    # output_path="output.avi"
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    images = []
    try:
        bilateral_activation_id = params["activation_id"]
        parts = params["parts"]
        # for i in range(0,parts):
        #     if os.path.exists(images_dir+'/resized_image_'+str(i)+'.jpg'):
        #         os.remove(images_dir+'/resized_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            bilateral_output = "bilateral-output-image"+bilateral_activation_id+"-"+str(i)
            load_image = pickle.loads(r.get(bilateral_output))
            image_name = 'Image'+str(i)+'.jpg'
            
            with open(image_name, 'wb') as f:
                f.write(load_image)
            images.append(image_name)
            
            
            # img =  cv2.imread(image_name)
            
            # resized_result.append('resized_image_'+str(i)+'.jpg')

    except Exception as e:
        image_url_list = params["image_url_links"]
        parts = len(image_url_list)
        for i in range(0,parts):
            response = requests.get(image_url_list[i])
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, "wb") as f:
                f.write(response.content)
            images.append(image_name)
            
            

    # input_images = os.listdir(path)

    # for i in input_images:
    #     i=path+i
    #     images.append(i)

    images.sort()

    # cv2_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    cv2_fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    frame = cv2.imread(images[0])

    size = list(frame.shape)
    
    del size[2]
    size.reverse()
    video = cv2.VideoWriter("output.avi",cv2_fourcc,3,size,1)
    
    for i in range(len(images)):
        video.write(cv2.imread(images[i]))
        print('frame',i+1,'of',len(images))
   
    video.release()

    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    
    bucket_name = 'dagit-store'

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=aws_region)

    s3.upload_file('output.avi', bucket_name, 'output.avi')
    s3.put_object_acl(Bucket=bucket_name, Key='output.avi', ACL='public-read')


    url = "https://dagit-store.s3.ap-south-1.amazonaws.com/output.avi"
   
    print(json.dumps({"encode_output": url,
                    "activation_id": activation_id,
                    "number_of_images_processed": parts,
                    }))


if __name__ == "__main__":
    main()