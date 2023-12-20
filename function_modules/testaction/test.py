#!/usr/bin/env python3

import os
import json
import sys
import boto3

def main():
    activation_id = os.environ.get('__OW_ACTIVATION_ID')

    # provider_ns = os.environ.get('PROVIDER_NS')
    # aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    # aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    # aws_region = os.getenv('AWS_REGION')
    # s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=aws_region)

    # print("Args----------",args)

    # # Retrieve information about the uploaded file from the trigger event
    # bucket_name = args['Records'][0]['s3']['bucket']['name']
    # object_key = args['Records'][0]['s3']['object']['key']

    # # Process the uploaded file (replace with your own code)
    # response = s3.get_object(Bucket=bucket_name, Key=object_key)
    # file_contents = response['Body'].read()
    # print('File contents:', file_contents)
    print(json.dumps({ "activation_id": str(activation_id),
                        "provider_ns": "test",
                       
                       "message":"Hello yayy"
                    }))

    return({"activation_id": str(activation_id),
            "provider_ns": "test",
            
            "message":"Hello yayy"
        })
    
    

if __name__ == "__main__":
    main()
