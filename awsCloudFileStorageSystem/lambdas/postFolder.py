import json
from .responses import *
import boto3
import base64
import uuid



def post_folder_dynamo(event, context):

    dynamodb_client = boto3.client('dynamodb')
    info = event['body']
    info_dict = json.loads(info)
    if info_dict['foldername'] is None or info_dict['username'] is None or info_dict['path'] is None:
        return {
            'statusCode': 400,
            'body': f'Failed to post folder. Please enter all fields.'
        }
    item_id = str(uuid.uuid4())
    try:
        response = dynamodb_client.put_item(
            TableName='folder-bivuja-table',
            Item={
                'id':{
                    'S': item_id
                },
                'foldername':{
                    'S': info_dict['foldername']
                },
                'username':{
                    'S': info_dict['username']
                },
                'path':{
                    'S': info_dict['path']
                }
            }
        )
        return {
            'statusCode': 200,
            'body': 'Folder uploaded successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Failed to upload folder: {str(e)}'
        }