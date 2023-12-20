#!/usr/bin/env python3
import os
from io import BytesIO
import cv2
import time
import numpy as np
import subprocess
import logging
import json
import sys
import paramiko
import pysftp

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

    contour_directory = "contoured-images"
    is_contour_dir = os.path.isdir(contour_directory)
    if(is_contour_dir == False):
        os.mkdir(contour_directory)

    images_dir = "images"
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)

    
    remote_download_path = "/home/faasapp/Desktop/anubhav/sprocket-decode/"+images_dir

    remote_upload_path = "/home/faasapp/Desktop/anubhav/contour-finding/"+contour_directory

    try:
        sftp.chdir(remote_download_path)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_download_path)  # Create remote_path
        sftp.chdir(remote_download_path)

    try:
        sftp.chdir(remote_upload_path)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_upload_path)  # Create remote_path
        sftp.chdir(remote_upload_path)

    sftp.get_d(remote_download_path,preserve_mtime=True,localdir=images_dir)

    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    
    decode_activation_id = params["activation_id"]
    parts = params["parts"]
    image_contour_mappings = {}
    contour_detected_images = {}
    for i in range(0,parts):
        img_name = images_dir+'/Image' + str(i) + '.jpg'
        img =  cv2.imread(img_name)
        img = cv2.resize(img,None,fx=0.9,fy=0.9)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(binary, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        contour_list_for_each_image=[]
        cv2.drawContours(img, contours, -1, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.01* cv2.arcLength(contour, True), True)
            contour_list_for_each_image.append(len(approx))


        image_contour_mappings[img_name] = sum(contour_list_for_each_image)
        filename = 'contour' + str(i) +'.jpg'
        # Saving the image
        cv2.imwrite(contour_directory+"/"+filename, img)
        contour_img = cv2.imread(contour_directory+"/"+filename)
        # contour_height, contour_width = contour_img.shape[:2]
        contour_detected_size = os.stat(contour_directory+"/"+filename).st_size
        contour_detected_images[contour_directory+"/"+filename] = contour_detected_size
    
    current_path = os.getcwd()
    sftp.put_d(current_path+"/"+contour_directory,preserve_mtime=True,remotepath=remote_upload_path)
    contour_images = os.listdir(current_path+"/"+contour_directory)
    end = time1.time()
    exec_time = end-start
    decode_execution_time = params["exec_time_decode"]
    print(json.dumps({ "contour_images": contour_images,
                        "image_contour_mappings": image_contour_mappings,
                        "contour_detect_activation_id": str(activation_id),
                        "number_of_images_processed": parts,
                        "contour_execution_time": exec_time,
                        "decode_execution_time": decode_execution_time,
                        "contour_detected_images_size": contour_detected_images
                    }))
    

if __name__ == "__main__":
    main()