import json
import boto3
import base64

def delete_file(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    bucket_name = event['pathParameters']['bucket']
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
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

