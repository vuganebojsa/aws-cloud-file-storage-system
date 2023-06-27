import json
from .responses import *
import boto3

def send_invite(event, context):

    dynamodb_client = boto3.client('dynamodb')
    info = event['body']

    info_dict = json.loads(info)
    if info_dict.get('inviter') is None or info_dict.get('familyMember') is None:
        return get_return('Invalid params', 400)
    if info_dict.get('inviter') == info_dict.get('familyMember'):
        return get_return('Cant invite yourself.', 400)
    
    user = get_user_by_email(info_dict.get('familyMember'))
    if user is not None:
        return get_return('User with given email already exists.', 400)
    
    dynamodb = boto3.client('dynamodb')

    resp = dynamodb.get_item(
            TableName='invite-bivuja-table',
            Key={
                'id': {'S': info_dict['inviter'] + '/' + info_dict['familyMember']}
            }
        )
    # Check if the record exists
    if 'Item' in resp:
        return get_return('Family member already invited.', 400)
    
    
    try:
        response = dynamodb_client.put_item(
            TableName='invite-bivuja-table',
            Item={
                'id':{
                    'S': info_dict['inviter'] + '/' + info_dict['familyMember']
                },
                'status':{
                    'S': 'pending'
                }
            }
        )
        send_email(info_dict['familyMember'], 'You have been invited to join our file storage app!', 'Click on the link below and register yourself!\n http://localhost:4200/register-from-invite/')
        return get_return('Invite sent successfully!', 200)
    except Exception as e:
        print(e)
        return get_return('Failed to send invite to user. Key error ', 400)
    


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


def get_user_by_email(email):
    client = boto3.client('cognito-idp', region_name='eu-central-1') 

    response = client.list_users(
        UserPoolId='eu-central-1_JywQCrS95',
        Filter=f'email = "{email}"'
    )
    users = response['Users']
    if users is None:
        return None
    if len(users) == 0:
        return None
    return 1
