import json
import boto3
import base64

dynamodb = boto3.resource('dynamodb')


def save_item_to_destination_table(item):
    destination_table_name = 'consistency-bivuja-table'

    destination_table = dynamodb.Table(destination_table_name)
    response = destination_table.put_item(Item=item)
    return response

def get_item_by_id(item_id):
    
    table_name = 'folder-bivuja-table'
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key={
            'id': item_id
        }
    )
    item = response.get('Item')
    return item


def delete_folder_dynamo(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    bucket_name = event['pathParameters']['bucket']
    username = event['pathParameters']['username']
    file_id = event['pathParameters']['id']

    item_to_save = get_item_by_id(file_id)
    save_item_to_destination_table(item_to_save)

    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(
            TableName='folder-bivuja-table',
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

