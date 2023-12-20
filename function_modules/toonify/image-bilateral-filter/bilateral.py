#!/usr/bin/env python3
import requests
import os
import boto3
import redis
import pickle
import json
import cv2
import sys

def main():
    images_dir = "bilateral-images"
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    bilateral_result = []
    try:
        decode_activation_id = params["activation_id"]
        parts = params["parts"]
        for i in range(0,parts):
            if os.path.exists(images_dir+'/bilateral_filtered_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/bilateral_filtered_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            decode_output = "decode-output-image"+decode_activation_id+"-"+str(i)
            load_image = pickle.loads(r.get(decode_output)) # Read from redis
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, 'wb') as f:
                f.write(load_image)
            
            originalmage =  cv2.imread(image_name)

            ReSized1 = cv2.resize(originalmage, (720, 640))
            grayScaleImage = cv2.cvtColor(originalmage, cv2.COLOR_BGR2GRAY)
            ReSized2 = cv2.resize(grayScaleImage, (720, 640))
            #applying median blur to smoothen an image
            smoothGrayScale = cv2.medianBlur(grayScaleImage, 5)
            ReSized3 = cv2.resize(smoothGrayScale, (720, 640))
            #retrieving the edges for cartoon effect
            getEdge = cv2.adaptiveThreshold(smoothGrayScale, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            ReSized4 = cv2.resize(getEdge, (720, 640))
            #applying bilateral filter to remove noise and keep edge sharp as required
            colorImage = cv2.bilateralFilter(originalmage, 9, 300, 300)
            ReSized5 = cv2.resize(colorImage, (720, 640))
            #masking edged image with our "BEAUTIFY" image
            cartoonImage = cv2.bitwise_and(colorImage, colorImage, mask=getEdge)
            cartoon_image = cv2.resize(cartoonImage, (720, 640))

           
            output_image = images_dir+'/bilateral_filtered_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, cartoon_image)

            img = open(output_image,"rb").read()
            pickled_object = pickle.dumps(img)
            bilateral_output = "bilateral-output-image"+activation_id+"-"+str(i)
            r.set(bilateral_output,pickled_object)
            
            bilateral_result.append('bilateral_filtered_image_'+str(i)+'.jpg')
        print(json.dumps({"bilateral_filtered_image_links":bilateral_result,
                            "activation_id": str(activation_id),
                            "parts": parts
                            
                        }))

        return({"bilateral_filtered_image_links":bilateral_result,
                "activation_id": str(activation_id),
                "parts": parts
            })


    except Exception as e: # If not running as a part of DAG workflow and implemented as a single standalone function
        image_url_list = params["image_url_links"]
        parts = len(image_url_list)
        for i in range(0,parts):
            if os.path.exists(images_dir+'/bilateral_filtered_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/bilateral_filtered_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            response = requests.get(image_url_list[i])
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, "wb") as f:
                f.write(response.content)


            originalmage =  cv2.imread(image_name)

            ReSized1 = cv2.resize(originalmage, (720, 640))
            grayScaleImage = cv2.cvtColor(originalmage, cv2.COLOR_BGR2GRAY)
            ReSized2 = cv2.resize(grayScaleImage, (720, 640))
            #applying median blur to smoothen an image
            smoothGrayScale = cv2.medianBlur(grayScaleImage, 5)
            ReSized3 = cv2.resize(smoothGrayScale, (720, 640))
            #retrieving the edges for cartoon effect
            getEdge = cv2.adaptiveThreshold(smoothGrayScale, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            ReSized4 = cv2.resize(getEdge, (720, 640))
            #applying bilateral filter to remove noise and keep edge sharp as required
            colorImage = cv2.bilateralFilter(originalmage, 9, 300, 300)
            ReSized5 = cv2.resize(colorImage, (720, 640))
            #masking edged image with our "BEAUTIFY" image
            cartoonImage = cv2.bitwise_and(colorImage, colorImage, mask=getEdge)
            cartoon_image = cv2.resize(cartoonImage, (720, 640))

           
            output_image = images_dir+'/bilateral_filtered_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, cartoon_image)
            bilateral_result.append('bilateral_filtered_image_'+str(i)+'.jpg')
   

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
        for image in bilateral_result:
            url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
            url_list.append(url)
                
        print(json.dumps({"bilateral_filtered_image_links":url_list,
                            "activation_id": str(activation_id),
                            "parts": parts
                            
                        }))

        return({"bilateral_filtered_image_links":url_list,
                "activation_id": str(activation_id),
                "parts": parts
                
            })

if __name__ == "__main__":
    main()