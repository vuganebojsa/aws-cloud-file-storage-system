import json
import boto3
import base64

dynamodb = boto3.resource('dynamodb')


def save_item_to_destination_table(item):
    destination_table_name = 'consistency-bivuja-table'
    item['mode'] = 'delete'
    
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


def delete_file(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    # filename as base64 coded bcz of paths
    # /{bucket}/{id}/{username}/{filename}
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')

    response = delete_from_dynamo(event)
    if response is None:
        response = delete_from_s3(event)
    else:
        send_email(event['headers']['useremail'],'Failed to delete file:' + file_name, 'Failed to delete file:' + file_name)

    return response


def delete_from_dynamo(event):
    bucket_name = event['pathParameters']['bucket']
    username = event['pathParameters']['username']
    file_id = event['pathParameters']['id']
    if file_id is None:
        return get_return('Failed to delete file. Invalid parameters', 400)

    item_to_save = get_item_by_id(file_id)
    retval = save_item_to_destination_table(item_to_save)
    if retval is not None:
        return get_return('Invalid file id. Please try again.', 401)
    
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(
            TableName='bivuja-table',
            Key={
                'id': {'S': file_id},
            }
        )
    except Exception as e:
       return get_return('Failed to delete file from dynamo', 500)
    return None

def delete_from_s3(event):
    bucket_name = event['pathParameters']['bucket']
    file_id = event['pathParameters']['id']
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')
    if file_name is None:
        item = get_item_by_id_consistency(file_id)
        db_cons = save_item_to_dynamodb(item)
        send_email(event['headers']['useremail'],'Failed to delete file:' + file_name, 'Failed to delete file:' + file_name)

        return get_return('File failed to delete.', 401)

    s3_client = boto3.client('s3')

    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code != 204:
            item = get_item_by_id_consistency(file_id)
            db_cons = save_item_to_dynamodb(item)
            if db_cons['ResponseMetadata']['HTTPStatusCode'] == 200:
                send_email(event['headers']['useremail'],'Failed to delete file:' + file_name, 'Failed to delete file:' + file_name)

                return get_return('Failde to delete file.', 401)
            else:
                send_email(event['headers']['useremail'],'Failed to delete file:' + file_name, 'Failed to delete file:' + file_name)
                return get_return('Something went wrong.', 500)

        send_email(event['headers']['useremail'],'Successfully deleted a file with name:' + file_name, 'Successfully deleted a file with name:' + file_name)

        return get_return('File deleted successfully.', 200)
    
    except Exception as e:
        item = get_item_by_id(file_id)
        db_cons = save_item_to_dynamodb(item)
        return get_return('Failed to delete file from S3 bucket.', 500)



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