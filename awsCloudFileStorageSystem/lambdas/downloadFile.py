import json
from .responses import *
import boto3
import base64


def download_file(event, context):
    # Set the region for the S3 bucket
    region = 'eu-central-1'
    
    # Set the name of the S3 bucket
    bucket_name = 'bivuja-bucket'
    
    # Set the path and filename of the file to download
    s3 = boto3.client('s3', region_name=region)
    fullpath = event['pathParameters']['fullpath']
    if fullpath is None:
        return {
        'statusCode': 400,
        'body': 'Error downloading file. Please enter full path'
        }
    # Download the file from S3
    try:
        response = s3.download_file(Bucket=bucket_name, Key=fullpath)
        file_content = response['Body'].read().decode('utf-8')

        print('File downloaded successfully.')
        return {
            'statusCode': 200,
            'body': file_content
        }
    except Exception as e:
        print('Error downloading file:', str(e))
        return {
            'statusCode': 500,
            'body': 'Error downloading file'
        }
