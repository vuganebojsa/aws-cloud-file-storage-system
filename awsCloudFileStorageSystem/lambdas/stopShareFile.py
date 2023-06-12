import json
import boto3
import base64


def stop_share_file(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name

    file_id = event['pathParameters']['id']


    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(
            TableName='content-share-bivuja-table',
            Key={
                'id': {'S': file_id},
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

