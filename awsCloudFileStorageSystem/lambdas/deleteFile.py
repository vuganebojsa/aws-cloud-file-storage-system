import json
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


def delete_file(event, context):
    # Replace 'YOUR_BUCKET_NAME' with your actual bucket name
    bucket_name = event['pathParameters']['bucket']
    file_id = event['pathParameters']['id']
    file_name = base64.b64decode(event['pathParameters']['filename']).decode('utf-8')
    if file_id is None or file_name is None or bucket_name is None:
        return get_return('File failed to delete.', 401)
    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        response_code = response['ResponseMetadata']['HTTPStatusCode']
        if response_code != 204:
            item = get_item_by_id(file_id)
            db_cons = save_item_to_dynamodb(item)
            if db_cons['ResponseMetadata']['HTTPStatusCode'] == 200:
                return get_return('Failde to delete file.', 401)
            else:
                return get_return('Something went wrong.', 500)

        send_email(event['headers']['useremail'],'Successfully deleted a file with name:' + file_name, 'Successfully deleted a file with name:' + file_name)

        return get_return('File deleted successfully.', 200)
    
    except Exception as e:
        item = get_item_by_id(file_id)
        db_cons = save_item_to_dynamodb(item)
        return get_return('Failed to delete file from S3 bucket.', 500)


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