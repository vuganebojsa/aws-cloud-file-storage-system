import json
from .responses import *
import boto3
import base64

def register_user(event, context):
    cognito_client = boto3.client('cognito-idp')
    info = event['body']


    #nebojsa@gmail.com/bogdan@gmail.com                 
    # mailInviter/mainFamilyMember
    # splitujemo
    # izvucemo inviter mail
    # vidimo da li se podudara iz tela zahteva
    # ako ne vrati mu 400 error
    # proveriti da li je status pending, ako nije opet 400 error
    # ako da smisljaj dalje logiku

    if info is None:
        return get_return('Failed to register user. Missing body.', 400)
    
    username = info['username']
    password = info['password']
    email = info['email']
    firstName = info['firstName']
    lastName = info['lastName']
    dateOfBirth = info['dateOfBirth']
    inviterEmail = info['inviterEmail']
    if username is None or password is None or email is None:
        return get_return('Failed to register user, invalid params', 400)
    
    user_attributes = [
    {'given_name': info['given_name'], 'family_name':info['family_name'], 'birthdate': info['birthdate'], email:info['email']},]

    try:
        response = cognito_client.sign_up(
            ClientId='your-client-id',  
            Username=username,
            Password=password,
            UserAttributes=user_attributes,
            ValidationData=[]
        )
        return {
            'statusCode': 200,
            'body': 'User registered successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Failed to register user: {str(e)}'
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
