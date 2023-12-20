#!/usr/bin/env python3
import os
import time
import json
import sys
import paramiko
import time
import pysftp
import logging

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

    edge_detect__directory = "edge-detected-images"
    is_edgedetect_dir = os.path.isdir(edge_detect__directory)
    if(is_edgedetect_dir == False):
        os.mkdir(edge_detect__directory)

    remote_download_path_contour = "/home/faasapp/Desktop/anubhav/contour-finding/"+contour_directory
    remote_download_path_edge_detection = "/home/faasapp/Desktop/anubhav/edge-detection/"+edge_detect__directory


    remote_upload_path_contour = "/home/faasapp/Desktop/anubhav/assemble_images/"+contour_directory
    remote_upload_path_edge_detect = "/home/faasapp/Desktop/anubhav/assemble_images/"+edge_detect__directory

    try:
        sftp.chdir(remote_download_path_contour)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_download_path_contour)  # Create remote_path
        sftp.chdir(remote_download_path_contour)

    try:
        sftp.chdir(remote_download_path_edge_detection)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_download_path_edge_detection)  # Create remote_path
        sftp.chdir(remote_download_path_edge_detection)

    try:
        sftp.chdir(remote_upload_path_contour)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_upload_path_contour)  # Create remote_path
        sftp.chdir(remote_upload_path_contour)

    try:
        sftp.chdir(remote_upload_path_edge_detect)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remote_upload_path_edge_detect)  # Create remote_path
        sftp.chdir(remote_upload_path_edge_detect)

    
    current_path = os.getcwd()

    sftp.get_d(remote_download_path_contour,preserve_mtime=True,localdir=contour_directory)
    sftp.put_d(current_path+"/"+contour_directory,preserve_mtime=True,remotepath=remote_upload_path_contour)

    sftp.get_d(remote_download_path_edge_detection,preserve_mtime=True,localdir=edge_detect__directory)
    sftp.put_d(current_path+"/"+edge_detect__directory,preserve_mtime=True,remotepath=remote_upload_path_edge_detect)
    
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    contour_mappings = params["value"][0]["image_contour_mappings"]

    contour_exec_time = params["value"][0]["contour_execution_time"]
    edge_detection_exec_time = params["value"][1]["edge_detection_execution_time"]
    decode_execution_time = params["value"][0]["decode_execution_time"]

    decode_images_sizes = params["value"][1]["decoded_images_size"]
    contour_image_sizes = params["value"][0]["contour_detected_images_size"]
    edge_detect_image_sizes = params["value"][1]["edge_detected_images_size"]

    sorted_by_decode_image_sizes = sorted(decode_images_sizes.items(), key=lambda x:x[1], reverse=True)
    sorted_contour_image_sizes = sorted(contour_image_sizes.items(), key=lambda x:x[1], reverse=True)
    sorted_by_edge_detect_image_sizes = sorted(edge_detect_image_sizes.items(), key=lambda x:x[1], reverse=True)

    highest_decode_image_size = sorted_by_decode_image_sizes[0][0]
    highest_contour_images = sorted_contour_image_sizes[0][0]
    highest_edge_detected_images = sorted_by_edge_detect_image_sizes[0][0]

    # edge_detection_output = params["value"][1]["edge_detection_output"]
    # contour_detection_output = params["value"][0]["contour_images"]

    sorted_images_by_no_of_contours = sorted(contour_mappings.items(), key=lambda x:x[1], reverse=True)
    highest_number_of_contour_line_image = sorted_images_by_no_of_contours[0][0]

    end = time1.time()
    assemble_exec_time = end-start

    
    
    print(json.dumps({ "assemble_activation_id": str(activation_id),
                        "contour_exec_time": contour_exec_time,
                        "assemble_exec_time": assemble_exec_time,
                        "edge_detect_time": edge_detection_exec_time,
                        "decode_time": decode_execution_time,
                        "contour_lines_image_mappings": contour_mappings,
                        "image_with_highest_number_of_contour_lines": highest_number_of_contour_line_image,
                        "decode_image_sizes": decode_images_sizes,
                        "contour_image_sizes": contour_image_sizes,
                        "edge_detected_image_sizes": edge_detect_image_sizes,
                        "highest_size_decode_image": highest_decode_image_size,
                        "highest_contour_image" : highest_contour_images,
                        "highest_edge_detected_image": highest_edge_detected_images
                    }))
    

if __name__ == "__main__":
    main()