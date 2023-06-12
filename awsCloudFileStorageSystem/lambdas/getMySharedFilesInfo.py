import json
from .responses import *
import boto3
import base64
from datetime import datetime


def get_my_shared_files_info(event, context):

    username = event['pathParameters']['username']

    # GET ALL PATHS FROM THE SHARE TABLE WHERE RECEIVER USERNAME == THE PARAMTERE ONE


    dynamodb = boto3.resource('dynamodb')
    table_name = 'content-share-bivuja-table'
    table = dynamodb.Table(table_name)


    filter_expression = boto3.dynamodb.conditions.Key('giver').eq(username)


    response = table.scan(FilterExpression=filter_expression)
    files = response['Items']
    
    print(files)
    # Return the list of files
    response_object = {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        "statusCode": 200,
        "body": json.dumps(files)
    }

    return response_object