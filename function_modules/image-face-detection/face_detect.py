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
    
    images_dir = "face-detected-images"
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)
    r = redis.Redis(host="10.129.28.219", port=6379, db=2)
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    face_detected_result = []
    try:
        decode_activation_id = params["activation_id"]
        parts = params["parts"]
        for i in range(0,parts):
            if os.path.exists(images_dir+'/face_detected_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/face_detected_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            decode_output = "decode-output-image"+decode_activation_id+"-"+str(i)
            load_image = pickle.loads(r.get(decode_output))
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, 'wb') as f:
                f.write(load_image)
            
            img =  cv2.imread(image_name)
            # Load Haar cascade for face detection
            face_cascade = cv2.CascadeClassifier('../haarcascade_frontalface_default.xml')

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw bounding boxes around faces
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)[]
                # face = img[y:y+h, x:x+w]
                # # Apply a Gaussian blur to the face ROI
                # blurred_face = cv2.GaussianBlur(face, (23, 23), 30)
                # # Replace the face ROI with the blurred face
                # img[y:y+h, x:x+w] = blurred_face
            output_image = images_dir+'/face_detected_image_'+str(i)+'.jpg'
            # face_blurred_image = images_dir+'/face_blurred_image_'+str(i)+'.jpg'

            cv2.imwrite(output_image, img)
            # cv2.imwrite(face_blurred_image, blurred_face)
            
            imag = open(output_image,"rb").read()
            pickled_object = pickle.dumps(imag)
            face_detected_output = "face-detected-image"+activation_id+"-"+str(i)
            print(pickled_object)
            r.set(face_detected_output,pickled_object)

            face_detected_result.append('face_detected_image_'+str(i)+'.jpg')
        
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
        for image in face_detected_result:
            url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
            url_list.append(url)
                
        print(json.dumps({"face_detected_image_url_links":url_list,
                            "activation_id": str(activation_id),
                            "parts": parts
                            
                            
                        }))

        return({"face_detected_image_url_links":url_list,
                "activation_id": str(activation_id),
                "parts": parts
                
                
            })

    except Exception as e: #If not running as a part of DAG workflow and implemented as a single standalone function
        image_url_list = params["image_url_links"]
        parts = len(image_url_list)
        for i in range(0,parts):
            if os.path.exists(images_dir+'/face_detected_image_'+str(i)+'.jpg'):
                os.remove(images_dir+'/face_detected_image_'+str(i)+'.jpg')
        for i in range(0,parts):
            response = requests.get(image_url_list[i])
            image_name = 'Image'+str(i)+'.jpg'
            with open(image_name, "wb") as f:
                f.write(response.content)
            img =  cv2.imread(image_name)
            # Load Haar cascade for face detection
            face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw bounding boxes around faces
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            output_image = images_dir+'/face_detected_image_'+str(i)+'.jpg'
            cv2.imwrite(output_image, img)

            face_detected_result.append('face_detected_image_'+str(i)+'.jpg')

    
        
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
        for image in face_detected_result:
            url = "https://dagit-store.s3.ap-south-1.amazonaws.com/"+images_dir+"/"+image
            url_list.append(url)
                
        print(json.dumps({"face_detected_image_url_links":url_list,
                            "activation_id": str(activation_id),
                            "parts": parts
                            
                        }))

        return({"face_detected_image_url_links":url_list,
                "activation_id": str(activation_id),
                "parts": parts,
                "pickled_object":pickled_object
                
            })

if __name__ == "__main__":
    main()