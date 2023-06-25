import json
import boto3
import base64
import uuid

dynamodb = boto3.resource('dynamodb')

def save_item_to_destination_table(item):
    destination_table_name = 'consistency-bivuja-table'
    item['mode'] = 'add'

    destination_table = dynamodb.Table(destination_table_name)
    try:
        response = destination_table.put_item(Item=item)
    except Exception as e:
        return e
    return None

def get_item_by_id(item_id):
    
    table_name = 'bivuja-table'
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key={
            'id': item_id
        }
    )
    item = response.get('Item')
    return item

def get_item_by_id_consistency(item_id):
    
    table_name = 'consistency-bivuja-table'
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key={
            'id': item_id
        }
    )
    item = response.get('Item')
    return item

def save_item_to_dynamodb(item):
    table = dynamodb.Table('bivuja-table')

    response = table.put_item(Item=item)
    return response


def post_folder(event, context):
    # filename as base64 coded bcz of paths
    # /{bucket}/{filename}
    # in event body we have now fileContent as filed in dictionary
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')

    response = add_to_dynamo(event)
    if response is None:
        response = add_to_s3(event)
    else:
        send_email(event['headers']['useremail'],'Failed to upload file:' + file_name, 'Failed to upload file:' + file_name)

    return response


def add_to_dynamo(event):
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

def add_to_s3(event):
    s3 = boto3.client('s3')
    bucket_name = event['pathParameters']['bucket']
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')

    # file content is the file itself coded in base64

    info_dict = json.loads(event['body'])
    body = base64.b64decode(info_dict['fileContent'])
    
    if body is None or event['headers']['useremail'] is None:
        return get_return('Failed to upload folder to S3 bucket.', 400)
    try:
        send_email(event['headers']['useremail'],'Successfully added a file with name: '+ file_name, 'Successfully added a file with name: '+ file_name)

        response = s3.put_object(Bucket=bucket_name, Key=file_name, Body = body)
        return get_return('File uploaded successfully!', 200)
    except Exception as e:
       return get_return('Key error. File upload failed.', 400)



def send_email(recipient, subject, message):
    client = boto3.client('ses', region_name='eu-central-1')  

    try:
        response = client.send_email(
            Source='nebojsavuga@gmail.com',  # Replace with your verified sender email
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message}}
            }
        )
    except Exception as e:
        print(e)

    return response['MessageId']

def get_return(body, code):
    {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': code,
            'body': body
        }  