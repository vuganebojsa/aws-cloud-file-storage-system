import json
from .responses import *
import boto3
import base64
from datetime import datetime

def get_files(event, context):
    # s3 = boto3.client('s3')
    #bucket_name = event['pathParameters']['bucket']
    username = event['pathParameters']['username']

    # objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=username+'-')
    # print(objects)
    # print('\n\n\n')
    # s3_files = objects['Contents']
    # for s3_file in s3_files:
    #     print(s3_file)

    # return {
    #     'statusCode': 200,
    #     'body': 'Success'
    # }

    dynamodb = boto3.resource('dynamodb')

    # Specify the table name
    table_name = 'bivuja-table'

    # Access the DynamoDB table
    table = dynamodb.Table(table_name)

    # Define the filter expression
    filter_expression = boto3.dynamodb.conditions.Key('username').eq(username)

    # Use the scan operation with the filter expression
    response = table.scan(FilterExpression=filter_expression)

    # Extract the items from the response
    files = response['Items']

    # Continue scanning if the response is paginated
    files_sorted = sorted(files, key=lambda x: datetime.strptime(x["createdAt"], "%m/%d/%Y, %H:%M:%S"), reverse=True)

    print(files_sorted)
    # Return the list of files
    response_object = {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        "statusCode": 200,
        "body": json.dumps(files_sorted)
    }

    return response_object