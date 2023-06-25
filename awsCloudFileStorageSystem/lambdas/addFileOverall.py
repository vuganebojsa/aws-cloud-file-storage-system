import json
import boto3
import base64
import uuid

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

dynamodb = boto3.resource('dynamodb')

def save_item_to_destination_table(item, mode):
    destination_table_name = 'consistency-bivuja-table'
    print(item)
    item['mode'] = {'S': mode}
    print(item)
    dynamodb_client = boto3.client('dynamodb')
    try:
        response = dynamodb_client.put_item(TableName=destination_table_name,
                Item=item)
    except Exception as e:
        print(e)
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

def delete_item_from_dynamo_db_table(item):
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(
                TableName='bivuja-table',
                Key={
                    'id': {'S': item['id']},
                }
            )
    except Exception as e:
        return get_return('Something went wrong with deleting file.', 400)
    return None

def revert_to_previous_version(item):
    table = dynamodb.Table('bivuja-table')
    try:
        response = table.update_item(
                Key={'id': item['id']},
                UpdateExpression='SET filename = :value1, description = :value2, tags = :value3, #tp = :value4, size = :value5, lastModifiedAt= :value6, bucketName = :value7, folderName = :value8',
                ExpressionAttributeValues={
                    ':value1': item['filename'],
                    ':value2': item['description'],
                    ':value3': item['tags'],
                    ':value4': item['type'],
                    ':value5': item['size'],
                    ':value6': item['lastModifiedAt'],
                    ':value7': item['bucketName'],
                    ':value8': item['folderName'],
                },
                ExpressionAttributeNames={
                    '#tp': 'type'
                }, 
                ReturnValues='ALL_NEW')
    except Exception as e:
        return get_return('Something went wrong.', 400)
    return None

def post_file(event, context):
    # filename as base64 coded bcz of paths
    # /{bucket}/{filename}
    # in event body we have now fileContent as filed in dictionary
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')
    mode = AddEditMode('add', '')
    response = add_to_dynamo(event, mode)
    if response['statusCode'] <= 204:
        response = add_to_s3(event, mode)
    else:
        send_email(event['headers']['useremail'],'Failed to upload file:' + file_name, 'Failed to upload file:' + file_name)
    
    return response


def add_to_dynamo(event, mode):
    
    dynamodb_client = boto3.client('dynamodb')
    info = event['body']
    info_dict = json.loads(info)
    item_id = str(uuid.uuid4())
    dynamodb = boto3.resource('dynamodb')
    mode.set_id(item_id)
    if info_dict is None or info_dict['filename'] is None or info_dict['username'] is None or info_dict['bucketName'] is None:
        return get_return('Invalid parameters', 400)
    if info_dict['folderName'] == '':
        info_dict['filename'] = info_dict['username'] + '-' + info_dict['filename']
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
        mode.set_mode('edit')
        mode.set_id(items[0]['id'])
        retval = save_item_to_destination_table({
            'id':{
                        'S': items[0]['id']
                    },
                    'filename':{
                        'S': items[0]['filename']
                    },
                    'description':{
                        'S': items[0]['description']
                    },'tags':{
                        'S': items[0]['tags']
                    },'type':{
                        'S': items[0]['type']
                    },'size':{
                        'S': items[0]['size']
                    },'createdAt':{
                        'S': items[0]['createdAt']
                    },'lastModifiedAt':{
                        'S': items[0]['lastModifiedAt']
                    },'username':{
                        'S': items[0]['username']
                    },'bucketName':{
                        'S': items[0]['bucketName']
                    },'folderName':{
                        'S': items[0]['folderName']
                    },
        }, 'edit')
        if retval is not None:
            return get_return('Failed to edit file. Param error.', 400)
        try:
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
            return get_return('Data edited successfully', 200)
        except Exception as e:
            print(e)
            retval = get_item_by_id_consistency(items[0])
            revert_to_previous_version(retval)
            return get_return('Failed to edit data', 400)
        
    else:
        mode.set_mode('add')
        mode.set_id(item_id)
        retval = save_item_to_destination_table({
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
        }, 'add')
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
            return get_return('File uploaded successfully!', 200)
        except Exception as e:
            retval = get_item_by_id_consistency(item_id)
            resp = delete_item_from_dynamo_db_table(retval)
            return get_return('Invalid parameters. File upload failed.', 400)

def add_to_s3(event, mode):
    s3 = boto3.client('s3')
    bucket_name = event['pathParameters']['bucket']
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')
    selected_mode = mode.get_mode()
    item_id = mode.get_id()
    # file content is the file itself coded in base64

    info_dict = json.loads(event['body'])
    body = base64.b64decode(info_dict['fileContent'])

    if body is None or event['headers']['useremail'] is None:

        retval = get_item_by_id_consistency(item_id)
        if selected_mode == 'add':
            delete_item_from_dynamo_db_table(retval)
        else:
            revert_to_previous_version(retval)
        return get_return('Failed to ' + selected_mode + ' in S3 bucket.', 400)
    

    try:
        response = s3.put_object(Bucket=bucket_name, Key=file_name, Body = body)
        send_email(event['headers']['useremail'],'Successfully added a file with name: '+ file_name, 'Successfully added a file with name: '+ file_name)

        return get_return('File uploaded successfully!', 200)
    except Exception as e:
        retval = get_item_by_id_consistency(item_id)
        if selected_mode == 'add':
            delete_item_from_dynamo_db_table(retval)
        else:
            revert_to_previous_version(retval)
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
    return {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': code,
            'body': body
        }  