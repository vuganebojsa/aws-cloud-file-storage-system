import json
from .responses import *
import boto3

def get_file(event, context):
    s3 = boto3.client('s3')
    print(event)
    bucket_name = event['pathParameters']['bucket']
    file_name = event['pathParameters']['filename']
    # body = {
    #     "message": "Go Serverless v1.0! Your function executed successfully!",
    #     "input": event
    # }

    response = {
        "statusCode": 200,
        "body": json.dumps({'bucket_name':bucket_name, 'file_name':file_name})
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
