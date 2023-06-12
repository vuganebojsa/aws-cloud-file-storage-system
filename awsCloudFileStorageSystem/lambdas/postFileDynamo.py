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
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('bivuja-table')
    response = table.scan(
        FilterExpression='filename = :filename and folderName = :folderName and bucketName = :bucketName AND #usr = :giver',
        ExpressionAttributeValues={
            ':filename': info_dict['filename'],
            ':giver': info_dict['username'],
            ':folderName':info_dict['folderName'],
            ':bucketName':info_dict['bucketName']
        },
        ExpressionAttributeNames={
            '#usr': 'username'
        }   )
    items = response['Items']
    if len(items) != 0:
        try:
            print('Usao')
            response = table.update_item(
            Key={'id': items[0]['id']},
            UpdateExpression='SET filename = :value1, description = :value2, tags = :value3, #tp = :value4, size = :value5, lastModifiedAt= :value6, bucketName = :value7, folderName = :value8',
            ExpressionAttributeValues={
                ':value1': info_dict['filename'],
                ':value2': info_dict['description'],
                ':value3': info_dict['tags'],
                ':value4': info_dict['type'],
                ':value5': info_dict['size'],
                ':value6': info_dict['lastModifiedAt'],
                ':value7': info_dict['bucketName'],
                ':value8': info_dict['folderName'],
            },
            ExpressionAttributeNames={
                '#tp': 'type'
            }, 
            ReturnValues='ALL_NEW')
            return {
                'statusCode': 200,
                'body': 'Data edited successfully.'
            }
        except Exception as e:
            print(e)

            return {
                'statusCode': 400,
                'body': f'Failed to edit data: {str(e)}'
            }
        
    else:
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
                'statusCode': 400,
                'body': f'Failed to upload data: {str(e)}'
            }