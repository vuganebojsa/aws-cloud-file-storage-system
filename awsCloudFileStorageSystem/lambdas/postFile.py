import json
from .responses import *
import boto3
import base64

def send_email(recipient, subject, message):
    client = boto3.client('ses', region_name='eu-central-1')  

    try:
        response = client.send_email(
            Source='nebojsavuga@gmail.com',  # Replace with your verified sender email
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message}}
            }
        )
    except Exception as e:
        print(e)

    return response['MessageId']

def post_file(event, context):
    s3 = boto3.client('s3')
    bucket_name = event['pathParameters']['bucket']
    file_name = event['pathParameters']['filename']
    body = base64.b64decode(event['body'])
    if body is None or file_name is None or bucket_name is None:
        return {
          'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
          'statusCode': 400,
          'body': 'Failed to upload file to S3 bucket.'
       }
    try:
        response = s3.put_object(Bucket=bucket_name, Key=file_name, Body = body)
        send_email(event['headers']['useremail'],'Successfully added a file to our system with name: ' + file_name, 'Successfully added a file to our system with name: ' + file_name)
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
    



