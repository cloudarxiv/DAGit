#!/usr/bin/env python3
import os
import time
import json
import sys
import paramiko
import time
import pysftp
import logging
import psutil

def main():
    
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
    is_images_dir = os.path.isdir(images_dir)
    if(is_images_dir == False):
        os.mkdir(images_dir)

    contour_directory = "contoured-images"
    is_contour_dir = os.path.isdir(contour_directory)
    if(is_contour_dir == False):
        os.mkdir(contour_directory)

    edge_detect__directory = "edge-detected-images"
    is_edgedetect_dir = os.path.isdir(edge_detect__directory)
    if(is_edgedetect_dir == False):
        os.mkdir(edge_detect__directory)

    remote_download_path_contour = "/home/faasapp/Desktop/anubhav/assemble_images/"+contour_directory
    remote_download_path_edge_detection = "/home/faasapp/Desktop/anubhav/assemble_images/"+edge_detect__directory
    remote_download_path_decode = "/home/faasapp/Desktop/anubhav/sprocket-decode/"+images_dir

    sftp.get_d(remote_download_path_contour,preserve_mtime=True,localdir=contour_directory)
    sftp.get_d(remote_download_path_edge_detection,preserve_mtime=True,localdir=edge_detect__directory)
    sftp.get_d(remote_download_path_decode,preserve_mtime=True,localdir=images_dir)

    no_of_images = len(os.listdir(images_dir))

    

    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])

    highest_contour_line_images = params["image_with_highest_number_of_contour_lines"]

    decode_execution_time = params["decode_time"]
    contour_exec_time = params["contour_exec_time"]
    edge_detection_exec_time = params["edge_detect_time"]
    assemble_exec_time = params["assemble_exec_time"]

    decode_image_sizes = params["decode_image_sizes"]
    contour_image_sizes = params["contour_image_sizes"]
    edge_detected_image_sizes = params["edge_detected_image_sizes"]

    highest_size_decode_image = params["highest_size_decode_image"]
    highest_contour_images_size = params["highest_contour_image"]
    highest_edge_detected_images_size = params["highest_edge_detected_image"]



    total_workflow_exec_time = decode_execution_time + max(contour_exec_time,edge_detection_exec_time) + assemble_exec_time

    contour_mappings = params["contour_lines_image_mappings"]

    print(json.dumps({ "performance_activation_id": str(activation_id),
                        "contour_exec_time": contour_exec_time,
                        "assemble_exec_time": assemble_exec_time,
                        "edge_detect_time": edge_detection_exec_time,
                        "decode_time": decode_execution_time,
                        "total_workflow_execution_time": total_workflow_exec_time,
                        "contour_lines_image_mappings": contour_mappings,
                        "image_with_highest_number_of_contour_lines": highest_contour_line_images,
                        "decode_image_sizes": decode_image_sizes,
                        "contout_image_sizes": contour_image_sizes,
                        "edge_detected_image_sizes": edge_detected_image_sizes,
                        "highest_size_decode_image": highest_size_decode_image,
                        "highest_contour_images_size" : highest_contour_images_size,
                        "highest_edge_detected_images_size": highest_edge_detected_images_size
                    }))
    

if __name__ == "__main__":
    main()