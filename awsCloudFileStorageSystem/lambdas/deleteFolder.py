import json
import boto3
import base64


dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')


def delete_s3_folder(bucket_name, folder_path):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

    if 'Contents' in response:
        for item in response['Contents']:
            object_key = item['Key']
            s3.delete_object(Bucket=bucket_name, Key=object_key)
        
        # Check if there are more objects to retrieve
        while response['IsTruncated']:
            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=folder_path,
                ContinuationToken=response['NextContinuationToken']
            )
            for item in response['Contents']:
                object_key = item['Key']
                s3.delete_object(Bucket=bucket_name, Key=object_key)
    else:
        print(f"No objects found in the folder: {folder_path}")

    # Delete the folder itself
    s3.delete_object(Bucket=bucket_name, Key=folder_path)

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


def delete_folder(event, context):

    # steps
    # save it in memory while deleting
    # so if i delete from folder-bivuja-table then i want it here while exceting to be saved for later 
    # revrite just in case
    # and so on
    # s3 also, for each file that i want to delete, i need to first save in memory somehow

    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    bucket_name = event['pathParameters']['bucket']
    file_id = event['pathParameters']['id']
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code != 204:
            item = get_item_by_id(file_id)
            db_cons = save_item_to_dynamodb(item)
            if db_cons['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {
          'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
          'statusCode': 401,
          'body': 'Failde to delete file.'
       }
        send_email(event['headers']['useremail'],'Successfully deleted a folder with name ' + file_name, 'Successfully deleted a folder with name ' + file_name)

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
        item = get_item_by_id(file_id)
        db_cons = save_item_to_dynamodb(item)
        return {
            'headers': {
                'Content-Type':'application/json',
                'Access-Control-Allow-Methods':'*',
                'Access-Control-Allow-Origin':'*'
            },
            'statusCode': 500,
            'body': 'Failed to upload file to S3 bucket.'
        }

