import json
from .responses import *
import boto3
import base64
import uuid

def share_file(event, context):

    dynamodb_client = boto3.client('dynamodb')
    info = event['body']
    #body
    # who is sharing,
    #  what is sharing?(path, if doesnt contain . its a folder, if it contains its a file), 
    # to who is sharing
    # content-share-bivuja-table
    # if shared folder just list the folder content and share it, without other folders, without other folders
    info_dict = json.loads(info)
    if info_dict.get('giver') is None or info_dict.get('receiver') is None or info_dict.get('path') is None:
        return get_return('Not all parameters were entered.', 400)
    item_id = str(uuid.uuid4())
    try:
        response = dynamodb_client.put_item(
            TableName='content-share-bivuja-table',
            Item={
                'id':{
                    'S': item_id
                },
                'giver':{
                    'S': info_dict['giver']
                },
                'receiver':{
                    'S': info_dict['receiver']
                },
                'path':{
                    'S': info_dict['path']
                }
            }
        )
        return get_return('File shared successfully', 200)
    except Exception as e:
        return get_return('Failed to share data', 401)
    

def get_return(body, code):
    return {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': code,
            'body': body
        }  