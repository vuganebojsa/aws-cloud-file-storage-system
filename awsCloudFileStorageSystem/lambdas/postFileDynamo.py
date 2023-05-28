import json
from .responses import *
import boto3
import base64
import uuid

def post_file_dynamo(event, context):

    dynamodb_client = boto3.client('dynamodb')
    info = event['body']
    info_dict = json.loads(info)
    item_id = str(uuid.uuid4())
    try:
        response = dynamodb_client.put_item(
            TableName='bivuja-table',
            Item={
                'id':{
                    'S': item_id
                },
                'filename':{
                    'S': info_dict['filename']
                },
                'description':{
                    'S': info_dict['description']
                },'tags':{
                    'S': info_dict['tags']
                },'type':{
                    'S': info_dict['type']
                },'size':{
                    'S': info_dict['size']
                },'createdAt':{
                    'S': info_dict['createdAt']
                },'lastModifiedAt':{
                    'S': info_dict['lastModifiedAt']
                },'username':{
                    'S': info_dict['username']
                },'bucketName':{
                    'S': info_dict['bucketName']
                },'folderName':{
                    'S': info_dict['folderName']
                },
            }
        )
        return {
            'statusCode': 200,
            'body': 'Data uploaded successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Failed to upload data: {str(e)}'
        }