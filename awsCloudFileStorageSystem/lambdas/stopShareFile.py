import json
import boto3
import base64


def stop_share_file(event, context):

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
            'body': 'File stoped sharing successfully.'
        }  
    except Exception as e:
       return {
          'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
          'statusCode': 400,
          'body': 'Failed to stop sharing file. Invalid File id.'
       }

