import json
import boto3
import base64

def delete_file_dynamo(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    bucket_name = event['pathParameters']['bucket']
    username = event['pathParameters']['username']

    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')
    folder_name = base64.b64decode(event['pathParameters']['foldername']).decode('utf-8')
    

    dynamodb_client = boto3.client('dynamodb')

    try:
        dynamodb_client.delete_item(
            TableName='bivuja-table',
            Key={
                'folderName': {'S': folder_name},
                'filename': {'S': file_name},
                'username': {'S': username},
                'bucketName':{'S':bucket_name}
            }
        )
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

