import json
from .responses import *
import boto3
import base64

def post_folder_s3(event, context):
    region = 'eu-central-1'
    
    # Set the name of the S3 bucket
    bucket_name = 'bivuja-bucket'
    
    # Set the desired directory path for the new folder
    #slash/slike
    
    # Create the S3 client
    s3 = boto3.client('s3', region_name=region)
    body = event['body']
    info_dict = json.loads(body)
    path = info_dict['path']
    
    # Create the folder (prefix) in the S3 bucket
    s3.put_object(Bucket=bucket_name, Key=path)
    
    return {
        'statusCode': 200,
        'body': 'S3 folder created successfully'
    }
    



