import json
from .responses import *
import boto3
import base64

def post_file(event, context):
    s3 = boto3.client('s3')
    bucket_name = event['pathParameters']['bucket']
    file_name = event['pathParameters']['filename']
    body = base64.b64decode(event['body'])
    try:
        response = s3.put_object(Bucket=bucket_name, Key=file_name, Body = body)
        return {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': 200,
            'body': 'File uploaded successfully.'
        }  
    except Exception as e:
       return {
          'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
          'statusCode': 500,
          'body': 'Failed to upload file to S3 bucket.'
       }
    



