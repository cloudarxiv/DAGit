#!/usr/bin/env python3
import requests
import os
import boto3
import redis
import pickle
import json
import cv2
import sys


# Removing noise from imagery — which is becoming more common in the field of image 
# processing and computer vision — is known as denoising.
# Image denoising uses advanced algorithms to remove noise from graphics and
# renders, making a huge difference to the quality of images.

def main():
    images_dir = "denoised-images"
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    denoised_result = []
    try:
        decode_activation_id = params["activation_id"]
        parts = params["parts"]
        for i in range(0,parts):
            if os.path.exists(images_dir+'/denoised_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/denoised_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            decode_output = "decode-output-image"+decode_activation_id+"-"+str(i)
            load_image = pickle.loads(r.get(decode_output))
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, 'wb') as f:
                f.write(load_image)
            
            img =  cv2.imread(image_name)
            denoised_image = cv2.bilateralFilter(img, 20, 100, 100)
            output_image = images_dir+'/denoised_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, denoised_image)
            denoised_result.append('denoised_image_'+str(i)+'.jpg')
            
        print(json.dumps({"denoised_image_url_links":denoised_result,
                        "activation_id": str(activation_id),
                        "parts": parts
                        
                    }))

        return({"denoised_image_url_links":denoised_result,
            "activation_id": str(activation_id),
            "parts": parts
            
        })
        
    except Exception as e: #If not running as a part of DAG workflow and implemented as a single standalone function
        image_url_list = params["image_url_links"]
        parts = len(image_url_list)
        for i in range(0,parts):
            if os.path.exists(images_dir+'/denoised_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/denoised_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            response = requests.get(image_url_list[i])
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, "wb") as f:
                f.write(response.content)
            img =  cv2.imread(image_name)
            denoised_image = cv2.bilateralFilter(img, 20, 100, 100)
            output_image = images_dir+'/denoised_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, denoised_image)
            denoised_result.append('denoised_image_'+str(i)+'.jpg')
            
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
        for image in denoised_result:
            url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
            url_list.append(url)
                
        print(json.dumps({"denoised_image_url_links":url_list,
                            "activation_id": str(activation_id),
                            "parts": parts
                            
                        }))

        return({"denoised_image_url_links":url_list,
                "activation_id": str(activation_id),
                "parts": parts
                
            })

if __name__ == "__main__":
    main()