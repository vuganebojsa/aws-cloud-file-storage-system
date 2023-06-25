import json
import boto3
import base64
import uuid

dynamodb = boto3.resource('dynamodb')
class AddEditMode(object):
    def __init__(self, mode, item_id):
        self.mode = mode
        self.item_id = item_id
    def get_mode(self):
        return self.mode
    def set_mode(self, mode):
        self.mode = mode
    def get_id(self):
        return self.item_id
    def set_id(self, mode):
        self.item_id = mode

def save_item_to_destination_table(item, mode):
    destination_table_name = 'consistency-bivuja-table'
    item['mode'] = 'add'

    destination_table = dynamodb.Table(destination_table_name)
    try:
        response = destination_table.put_item(Item=item)
    except Exception as e:
        return e
    return None

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
    table = dynamodb.Table('folder-bivuja-table')

    response = table.put_item(Item=item)
    return response

def delete_item_from_dynamo_db_table(item):
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(
                TableName='folder-bivuja-table',
                Key={
                    'id': {'S': item['id']},
                }
            )
    except Exception as e:
        return get_return('Something went wrong with deleting file.', 400)
    return None

def delete_from_consistency(item_id):
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(
            TableName='consistency-bivuja-table',
            Key={
                'id': {'S': item_id},
            }
        )
        return get_return('File deleted successfully', 200)
    except Exception as e:
       return get_return('Something went wrong. Key error.', 400)



def folder_exists(event):
    table = dynamodb.Table('folder-bivuja-table')
    response = table.scan(
        FilterExpression='foldername = :foldername and #pth = :path and #usr = :giver',
        ExpressionAttributeValues={
            ':foldername': event['foldername'],
            ':giver': event['username'],
            ':path':event['path']
        },
        ExpressionAttributeNames={
            '#usr': 'username',
            "#pth":'path'
        }   )
    items = response['Items']
    if len(items) > 0:
        return True
    return False

def post_folder(event, context):
    # filename as base64 coded bcz of paths
    # in event body we have now fileContent as filed in dictionary
    mode = AddEditMode('add', '')
    response = add_to_dynamo(event, mode)
    
    print(response)
    if response['statusCode'] <= 204:
        response = add_to_s3(event)
    else:
        send_email(event['headers']['useremail'],'Failed to upload folder' , 'Failed to upload folder')
    delete_from_consistency(mode.get_id())
    return response


def add_to_dynamo(event, mode):
    dynamodb_client = boto3.client('dynamodb')
    info = event['body']
    info_dict = json.loads(info)
    if info_dict['foldername'] is None or info_dict['username'] is None or info_dict['path'] is None:
        return get_return('Failed to add folder. Missing params', 400)
    if folder_exists(info_dict):
        return get_return('Folder already exists.', 400)
    item_id = str(uuid.uuid4())
    mode.set_id(item_id)
    try:
        info_dict['id'] = item_id
        save_item_to_destination_table(info_dict, 'add')
    except Exception as e:
        return get_return('Failed to upload folder to dynamo. Key error', 400)
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
        return get_return('Successfully uploaded a new folder.', 200)
    except Exception as e:

        return get_return('Failed to upload folder. Key Error', 400)
    

def add_to_s3(event):
    region = 'eu-central-1'
    
    # Set the name of the S3 bucket
    bucket_name = 'bivuja-bucket'
    
    # Set the desired directory path for the new folder
    #slash/slike
    
    # Create the S3 client
    s3 = boto3.client('s3', region_name=region)
    info = event['body']
    info_dict = json.loads(info)
    if info_dict['foldername'] is None or info_dict['username'] is None or info_dict['path'] is None:
        return get_return('Failed to add folder. Missing params', 400)
    if info_dict is None or info_dict['foldername'] is None or info_dict['username'] is None:
        return get_return('Failed to upload to s3. Invalid path', 400)
    fullpath = ''
    # maybe add / at the end
    if info_dict['path'] is not None and info_dict['path'] != '':
        fullpath = info_dict['username'] + '-' + info_dict['path'] + info_dict['foldername'] + '/'
    else:
        fullpath = info_dict['username'] + '-' + info_dict['foldername'] + '/'
    

    # Create the folder (prefix) in the S3 bucket
    try:
        response = s3.put_object(Bucket=bucket_name, Key=fullpath)
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code > 204:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('folder-bivuja-table')
            new_rep = table.scan(
                FilterExpression='foldername = :foldername AND path = :path AND #usr = :giver',
                ExpressionAttributeValues={
                    ':foldername': info_dict['foldername'],
                    ':giver': info_dict['username'],
                    ':path':info_dict['path']
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
                    return get_return('Folder failed to upload', 400)
                except Exception as e:
                    return get_return('Failed to upload folder.', 500)
        send_email(event['headers']['useremail'],'Successfully posted a folder with name ' + info_dict['foldername'], 'Successfully posted a folder with name ' + info_dict['foldername'])

        return get_return('Folder uploaded successfully', 200)
    except Exception as e:
       return get_return('Failed to upload to s3', 500)



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
    return {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': code,
            'body': body
        }  