import json
from .responses import *
import boto3
import base64

def check_invitation_status(event, context):
    info = event
    if info is None:
        return get_return('Failed to register user. Missing body.', 400)
    
    inviter_email = info['inviter_email']
    family_email = info['family_email']
    if inviter_email is None or family_email is None:
        return get_return('Invitation error.', 400)
    

    dynamodb = boto3.client('dynamodb')
    resp = dynamodb.get_item(
            TableName='invite-bivuja-table',
            Key={
                'id': {'S': inviter_email + '/' + family_email}
            }
        )
    if 'Item' not in resp:
        return get_return('Invalid email address. Please try again', 400)
    
    item = resp['Item']
    id_value = item['id']['S'].split('/')[0]
    status_value = item['status']['S']
    res = {'id':id_value, 'status':status_value}
    if res['status'] == 'pending':
        raise Exception('Status is still pending.')
    
    accepted = False
    if res['status'] == "accepted":
        accepted = True
    
    return {
        "status": accepted,
        "inviter_email":inviter_email,
        "family_email":family_email
    }

    



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


def get_user_by_username(username):
    client = boto3.client('cognito-idp', region_name='eu-central-1') 

    response = client.list_users(
        UserPoolId='eu-central-1_JywQCrS95',
        Filter=f'username = "{username}"'
    )
    users = response['Users']
    if users is None:
        return None
    if len(users) == 0:
        return None
    return 1
