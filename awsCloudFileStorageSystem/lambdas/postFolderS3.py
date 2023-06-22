import json
from .responses import *
import boto3
import base64


dynamodb = boto3.resource('dynamodb')

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



def get_item_by_id(item_id):
    
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

def post_folder_s3(event, context):
    region = 'eu-central-1'
    
    # Set the name of the S3 bucket
    bucket_name = 'bivuja-bucket'
    
    # Set the desired directory path for the new folder
    #slash/slike
    
    # Create the S3 client
    s3 = boto3.client('s3', region_name=region)
    body = event['body']
    info_dict = json.loads(body)
    path = info_dict['path']
    username, spl_path = path.split('-')
    p1 = ''
    foldername = ''
    if '/' in spl_path:
        p1,foldername = spl_path.rsplit('/', 1)
        p1 = p1 + '/'
    else:
        foldername = spl_path

    # Create the folder (prefix) in the S3 bucket
    try:
        response = s3.put_object(Bucket=bucket_name, Key=path)
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code > 204:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('folder-bivuja-table')
            new_rep = table.scan(
                FilterExpression='foldername = :foldername AND path = :path AND #usr = :giver',
                ExpressionAttributeValues={
                    ':foldername': foldername,
                    ':giver': username,
                    ':path':p1
                },
                ExpressionAttributeNames={
                    '#usr': 'username'
                }   )
            items = new_rep['Items']
            if len(items) != 0:
                dynamodb = boto3.client('dynamodb')
                try:
                    dynamodb.delete_item(
                        TableName='folder-bivuja-table',
                        Key={
                            'id': {'S': items[0]['id']},
                        }
                    )
                    send_email(event['headers']['useremail'],'Successfully posted a folder with name ' + foldername, 'Successfully posted a folder with name ' + foldername)

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
        send_email(event['headers']['useremail'],'Successfully posted a folder with name ' + foldername, 'Successfully posted a folder with name ' + foldername)

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
    
   



