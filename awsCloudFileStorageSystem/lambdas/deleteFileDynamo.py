import json
import boto3
import base64

def delete_file_dynamo(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    bucket_name = event['pathParameters']['bucket']
    username = event['pathParameters']['username']
    file_id = event['pathParameters']['id']


    dynamodb_client = boto3.client('dynamodb')

    try:
        dynamodb_client.delete_item(
            TableName='bivuja-table',
            Key={
                'ID': {'S': file_id},
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

