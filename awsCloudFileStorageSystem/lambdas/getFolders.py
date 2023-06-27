import json
from .responses import *
import boto3
import base64

def get_folders(event, context):
    # s3 = boto3.client('s3')
    #bucket_name = event['pathParameters']['bucket']
    username = event['pathParameters']['username']


    dynamodb = boto3.resource('dynamodb')

    # Specify the table name
    table_name = 'folder-bivuja-table'

    # Access the DynamoDB table
    table = dynamodb.Table(table_name)

    # Define the filter expression
    filter_expression = boto3.dynamodb.conditions.Key('username').eq(username)

    # Use the scan operation with the filter expression
    response = table.scan(FilterExpression=filter_expression)

    # Extract the items from the response
    files = response['Items']

    # Continue scanning if the response is paginated

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