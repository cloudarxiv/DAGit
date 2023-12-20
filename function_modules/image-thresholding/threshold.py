#!/usr/bin/env python3
import os
import requests
import boto3
import redis
import pickle
import json
import cv2
import sys
# Image thresholding is a simple, yet effective, 
# way of partitioning an image into a foreground and background. T
# his image analysis technique is a 
# type of image segmentation that isolates objects by converting grayscale images into binary images.
def main():
    images_dir = "thresholded-images"
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    thresholded_result = []
    try:
        decode_activation_id = params["activation_id"]
        parts = params["parts"]
        for i in range(0,parts):
            if os.path.exists(images_dir+'/thresholded_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/thresholded_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            decode_output = "decode-output-image"+decode_activation_id+"-"+str(i)
            load_image = pickle.loads(r.get(decode_output))
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, 'wb') as f:
                f.write(load_image)
            
            img =  cv2.imread(image_name)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            output_image = images_dir+'/thresholded_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, thresh)
            thresholded_result.append('thresholded_image_'+str(i)+'.jpg')
    except Exception as e: #If not running as a part of DAG workflow and implemented as a single standalone function
        image_url_list = params["image_url_links"]
        parts = len(image_url_list)
        for i in range(0,parts):
            if os.path.exists(images_dir+'/thresholded_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/thresholded_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            response = requests.get(image_url_list[i])
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, "wb") as f:
                f.write(response.content)
            img =  cv2.imread(image_name)

            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            output_image = images_dir+'/thresholded_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, thresh)
            thresholded_result.append('thresholded_image_'+str(i)+'.jpg')
            

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
    for image in thresholded_result:
        url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
        url_list.append(url)
            
    print(json.dumps({"thresholded_image_url_links":url_list,
                        "activation_id": str(activation_id),
                        "parts": parts
                        
                    }))

    return({"thresholded_image_url_links":url_list,
            "activation_id": str(activation_id),
            "parts": parts
            
        })

if __name__ == "__main__":
    main()