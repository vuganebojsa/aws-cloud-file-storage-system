import json
from .responses import *
import boto3
import base64
import uuid

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


dynamodb = boto3.resource('dynamodb')


def save_item_to_destination_table(item):
    destination_table_name = 'consistency-bivuja-table'

    destination_table = dynamodb.Table(destination_table_name)
    response = destination_table.put_item(Item=item)
    return response

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
    table = dynamodb.Table('folder-bivuja-table')

    response = table.put_item(Item=item)
    return response


def move_file_s3(original_path, new_path, filename, username):
    source_bucket = 'bivuja-bucket'
    destination_bucket = 'bivuja-bucket'
    if username + '-' not in filename:
        source_key = username + '-' +  original_path + '/' + filename  # Path of the file to be moved
        destination_key = username + '-' + new_path + '/' + filename  # Destination path for the file
    else:
        source_key = filename
        new_filename = filename.split('-')[1]
        destination_key = username + '-' + new_path + '/' + new_filename  # Destination path for the file

    print(source_key)
    print(destination_key)
    s3_client = boto3.client('s3', region_name='eu-central-1')

    # Copy the file to the destination folder
    
    try:
    # Copy the file to the destination folder
        response = s3_client.copy_object(
            Bucket=destination_bucket,
            CopySource={'Bucket': source_bucket, 'Key': source_key},
            Key=destination_key
        )
        print("File copied successfully!")
    except Exception as e:
        print("An error occurred while copying the file:")
        print(e.response['Error']['Message'])
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        print(response_code)
    response_code = response['ResponseMetadata']['HTTPStatusCode']

    if response_code <= 204:
    # Delete the file from the source folder
        response = s3_client.delete_object(
                Bucket=source_bucket,
                Key=source_key
            )
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code > 204:
            return False
        return True
    return False

def move_file(event, context):

    dynamodb_client = boto3.client('dynamodb')
    info = event['body']
    info_dict = json.loads(info)
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('bivuja-table')
    old_folder_name = info_dict['folderName']
    new_folder_name = info_dict['newPathName']
    filename = info_dict['filename']
    if old_folder_name is None or new_folder_name is None or filename is None:
        return {
                        'statusCode': 400,
                        'body': 'Failed to move file.'
                    }
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
            save_item_to_destination_table(items[0])
            print('Prosao upis u consistency')
            if info_dict['folderName'] == '':
                new_filename = info_dict['filename'].split('-')[1]
                response = table.update_item(
                Key={'id': items[0]['id']},
                UpdateExpression='SET folderName = :value8, filename= :new_filename',
                ExpressionAttributeValues={
                    ':value8': info_dict['newPathName'],
                    ':new_filename': new_filename
                },
                ReturnValues='ALL_NEW')
            else:
                response = table.update_item(
                Key={'id': items[0]['id']},
                UpdateExpression='SET folderName = :value8',
                ExpressionAttributeValues={
                    ':value8': info_dict['newPathName']
                },
                ReturnValues='ALL_NEW')
            print('Prosao upis u dynamo update')
            response_code = response['ResponseMetadata']['HTTPStatusCode']
            print(response_code)

            if response_code <= 204:
                s3_move_success = move_file_s3(old_folder_name, new_folder_name, filename, info_dict['username'])
                print(s3_move_success)
                if s3_move_success is True:
                    send_email(event['headers']['useremail'],'Successfully moved a file', 'Successfully moved a file from ' + old_folder_name + ' to' + new_folder_name)

                    return {
                        'statusCode': 200,
                        'body': 'Data edited successfully.'
                    }
                else:
                    response = table.update_item(
                    Key={'id': items[0]['id']},
                    UpdateExpression='SET folderName = :value8',
                    ExpressionAttributeValues={
                        ':value8': old_folder_name
                    },
                    ReturnValues='ALL_NEW')
                    return {
                        'statusCode': 200,
                        'body': 'Data edited successfully.'
                    }
        except Exception as e:
            print('Usao u exception')
            response = table.update_item(
                    Key={'id': items[0]['id']},
                    UpdateExpression='SET folderName = :value8',
                    ExpressionAttributeValues={
                        ':value8': old_folder_name
                    },
                    ReturnValues='ALL_NEW')

            return {
                'statusCode': 400,
                'body': f'Failed to edit data: {str(e)}'
            }
        
    
    return {
        'statusCode': 400,
        'body': f'Failed to upload data: {str(e)}'
    }