#!/usr/bin/env python3
import os
import redis
import requests 
import boto3
import pickle
import cv2
import time
import subprocess
import json
import sys

def main():
    images_dir = "edge-detected-images"
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    # edge_detected_images = {}
    edge_detected_result = []
    try:
        decode_activation_id = params["activation_id"]
        parts = params["parts"]
        for i in range(0,parts):
            if os.path.exists(images_dir+'/edge_detected_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/edge_detected_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            decode_output = "decode-output-image"+decode_activation_id+"-"+str(i)
            load_image = pickle.loads(r.get(decode_output))
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, 'wb') as f:
                f.write(load_image)
            
            img =  cv2.imread(image_name)
            # height, width = img.shape[:2]
            # size = os.stat(img_name).st_size
            # decoded_images_sizes[img_name] = size
            image= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            canny_output = cv2.Canny(image, 80, 150)
            output_image = images_dir+'/edge_detected_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, canny_output)
            edge_detected_result.append('edge_detected_image_'+str(i)+'.jpg')
    except Exception as e: #If not running as a part of DAG workflow and implemented as a single standalone function
        image_url_list = params["image_url_links"]
        parts = len(image_url_list)
        for i in range(0,parts):
            if os.path.exists(images_dir+'/edge_detected_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/edge_detected_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            response = requests.get(image_url_list[i])
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, "wb") as f:
                f.write(response.content)
            img =  cv2.imread(image_name)
            image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            canny_output = cv2.Canny(image, 80, 150)
            output_image = images_dir+'/edge_detected_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, canny_output)
            edge_detected_result.append('edge_detected_image_'+str(i)+'.jpg')
   

    
        
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
    for image in edge_detected_result:
        url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
        url_list.append(url)
            
    print(json.dumps({"edge_detected_image_url_links":url_list,
                        "activation_id": str(activation_id),
                        "number_of_images": parts
                        
                    }))

    return({"edge_detected_image_url_links":url_list,
            "activation_id": str(activation_id),
            "number_of_images": parts
            
        })

if __name__ == "__main__":
    main()


    

    
    
    
    
    
    
    
    
    
    

    

    
    
    # decode_activation_id = params["activation_id"]
    # decoded_images_sizes = {}
    # edge_detected_images = {}
    # parts = params["parts"]
    # for i in range(0,parts):
    #     img_name = images_dir+'/Image' + str(i) + '.jpg'
    #     img =  cv2.imread(img_name)
    #     # height, width = img.shape[:2]
    #     size = os.stat(img_name).st_size
    #     decoded_images_sizes[img_name] = size
    #     image= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     canny_output = cv2.Canny(image, 80, 150)

    #     filename = 'detected-edges-' + str(i) +'.jpg'
    #     # Saving the image
    #     cv2.imwrite(edge_detect__directory+"/"+filename, canny_output)

    #     edge_img = cv2.imread(edge_detect__directory+"/"+filename)
    #     # edge_height, edge_width = edge_img.shape[:2]

    #     edge_detected_size = os.stat(edge_detect__directory+"/"+filename).st_size
    #     edge_detected_images[edge_detect__directory+"/"+filename] = edge_detected_size
    
    # current_path = os.getcwd()
    # sftp.put_d(current_path+"/"+edge_detect__directory,preserve_mtime=True,remotepath=remote_upload_path)
    # detected_edge_images = os.listdir(current_path+"/"+edge_detect__directory)
    # print(json.dumps({ "edge_detection_output": detected_edge_images,
    #                     "edge_detect_activation_id": str(activation_id),
    #                     "number_of_images_processed": parts,
    #                     "edge_detection_execution_time": exec_time,
    #                     "decode_execution_time": decode_execution_time,
    #                     "edge_detected_images_size": edge_detected_images,
    #                     "decoded_images_size": decoded_images_sizes
    #                 }))
    

