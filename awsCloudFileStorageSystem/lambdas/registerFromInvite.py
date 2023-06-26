import json
from .responses import *
import boto3
import base64

def register_from_invite(event, context):
    cognito_client = boto3.client('cognito-idp')
    info = json.loads(event['body'])

    if info is None:
        return get_return('Failed to register user. Missing body.', 400)
    
    username = info['username']
    password = info['password']
    email = info['email']
    firstName = info['name']
    lastName = info['surname']
    dateOfBirth = info['birthDate']
    inviterEmail = info['inviterEmail']
    if username is None or password is None or email is None or firstName is None or lastName is None or dateOfBirth is None or inviterEmail is None:
        return get_return('Failed to register user, invalid params', 400)
    
    usr = get_user_by_username(username)
    if usr is not None:
        return get_return('User with username: ' + username + ' already exists.', 400)

    dynamodb = boto3.client('dynamodb')
    resp = dynamodb.get_item(
            TableName='invite-bivuja-table',
            Key={
                'id': {'S': inviterEmail + '/' + email}
            }
        )
    if 'Item' not in resp:
        return get_return('Invalid email address. Please try again', 400)
    
    item = json.loads(resp['Item'])
    if item['status'] != 'pending':
        return get_return('This request has already been processed.', 400)


    user_attributes = [
    {'given_name': firstName, 'family_name':lastName, 'birthdate': dateOfBirth, email:email},]

    try:
        response = cognito_client.sign_up(
            ClientId='eu-central-1_JywQCrS95',  
            Username=username,
            Password=password,
            UserAttributes=user_attributes,
            ValidationData=[]
        )

        return get_return('Registration successfully. Wait for the inviter to respond.', 200)
    except Exception as e:
        return get_return('Failed to register. Invalid attributes.', 400)



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
