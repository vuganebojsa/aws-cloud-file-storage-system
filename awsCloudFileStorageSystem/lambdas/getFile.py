import json
from .responses import *
import boto3
import base64

def get_file(event, context):
    s3 = boto3.client('s3')
    print(event)
    bucket_name = event['pathParameters']['bucket']
    file_name = event['pathParameters']['filename']
    
    try:
        s3.head_object(Bucket=bucket_name, Key= file_name)
    except Exception:
        return get_404_response('{"message":"File not found"}')
    
    my_file = s3.get_object(Bucket=bucket_name, Key=file_name)
    content = my_file['Body'].read()
    
    
    if content is not None:
         return {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': 200,
            'body': base64.b64encode(content).decode('utf-8'),
            'isBase64Encoded': True
        }  
    else:
        return get_404_response('{"message":"File not found"}')


