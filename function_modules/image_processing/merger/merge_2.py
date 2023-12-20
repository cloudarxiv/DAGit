#!/usr/bin/env python3

import os
import redis
import json
import sys

def main():
    
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    
    params = json.loads(sys.argv[1])
    
    responses_list = params["__ow_body"]
    
    found_dict = None
    for responses_dict in responses_list:
        if "thresholded_image_url_links" in responses_dict:
                found_dict = responses_dict
                thresholded_images = found_dict["thresholded_image_url_links"]
                break
     
    found_dict = None

    for responses_dict in responses_list:
        if "blurred_image_url_links" in responses_dict:
                found_dict = responses_dict
                blurred_images = found_dict["blurred_image_url_links"]
                break
        
    found_dict = None

    for responses_dict in responses_list:
        if "rotated_image_url_links" in responses_dict:
                found_dict = responses_dict
                rotated_images = found_dict["rotated_image_url_links"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "histogram_image_url_links" in responses_dict:
                found_dict = responses_dict
                histogram_images = found_dict["histogram_image_url_links"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "histogram_image_url_links" in responses_dict:
                found_dict = responses_dict
                histogram_images = found_dict["histogram_image_url_links"]
                break
            
    found_dict = None

    for responses_dict in responses_list:
        if "denoised_image_url_links" in responses_dict:
                found_dict = responses_dict
                denoised_images = found_dict["denoised_image_url_links"]
                break
    

            
    print(json.dumps({"activation_id": str(activation_id),               
                      "rotated_image_url_links":rotated_images,
                      "blurred_image_url_links": blurred_images,
                      "thresholded_image_url_links":thresholded_images,
                      "histogram_image_url_links":histogram_images,
                      "denoised_image_url_links":denoised_images
                    }))

    
    return({"activation_id": str(activation_id),
                "rotated_image_url_links":rotated_images,
                "blurred_image_url_links": blurred_images,
                "thresholded_image_url_links":thresholded_images,
                "histogram_image_url_links":histogram_images,
                "denoised_image_url_links":denoised_images
            })    
        
        
        
        
    
if __name__ == "__main__":
    main()