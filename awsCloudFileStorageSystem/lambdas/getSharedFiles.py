import json
from .responses import *
import boto3
import base64
from datetime import datetime



def query_table_with_multiple_keys(folder_name, giver):
    table_name = 'bivuja-table'
    dynamodb = boto3.resource('dynamodb')

    # Access the DynamoDB table
    table = dynamodb.Table(table_name)
    response = table.scan(
       FilterExpression='folderName = :folder_name AND #usr = :giver',
        ExpressionAttributeValues={
            ':folder_name': folder_name,
            ':giver': giver
        },
        ExpressionAttributeNames={
            '#usr': 'username'
        }
    )

    items = response['Items']
    # Process the items as needed
    return items

def query_table_filename(filename, giver):
    table_name = 'bivuja-table'
    dynamodb = boto3.resource('dynamodb')
    folder_path = ''
    file_name = filename
    if '/' in filename:
        split_string = filename.rsplit('/', 1)
        folder_path = split_string[0]
        file_name = split_string[1]
    # Access the DynamoDB table
    table = dynamodb.Table(table_name)
    response = table.scan(
        FilterExpression='filename = :filename and folderName = :folderName AND #usr = :giver',
        ExpressionAttributeValues={
            ':filename': file_name,
            ':giver': giver,
            ':folderName':folder_path
        },
        ExpressionAttributeNames={
            '#usr': 'username'
        }   )

    items = response['Items']
    # Process the items as needed
    return items

def get_shared_files(event, context):

    username = event['pathParameters']['username']

    # GET ALL PATHS FROM THE SHARE TABLE WHERE RECEIVER USERNAME == THE PARAMTERE ONE


    dynamodb = boto3.resource('dynamodb')
    table_name = 'content-share-bivuja-table'
    table = dynamodb.Table(table_name)


    filter_expression = boto3.dynamodb.conditions.Key('receiver').eq(username)


    response = table.scan(FilterExpression=filter_expression)
    files = response['Items']
    
    table_name = 'bivuja-table'
    table = dynamodb.Table(table_name)

    filtered_files = []
    for file in files:
        if '.' in file['path']:
            # get only file
            item = query_table_filename(file['path'], file['giver'])
            if len(item) != 0:
                
                filtered_files.append(item[0])
        else:
            items = query_table_with_multiple_keys(file['path'], file['giver'])
            if len(items) != 0:
                for item in items:
                    filtered_files.append(item)



    print(filtered_files)
    no_duplicates = []
    for f in filtered_files:
        if f not in no_duplicates:
            no_duplicates.append(f)
    # Return the list of files
    response_object = {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        "statusCode": 200,
        "body": json.dumps(no_duplicates)
    }

    return response_object