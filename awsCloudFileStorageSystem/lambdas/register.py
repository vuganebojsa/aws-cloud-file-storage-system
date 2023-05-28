import json
from .responses import *
import boto3
import base64

def register_user(event, context):
    cognito_client = boto3.client('cognito-idp')
    info = event['body']
    username = info['username']
    password = info['password']
    email = info['email']
    user_attributes = [
    {'given_name': info['given_name'], 'family_name':info['family_name'], 'birthdate': info['birthdate'], email:info['email']},]

    try:
        response = cognito_client.sign_up(
            ClientId='your-client-id',  # Replace with your Cognito User Pool App Client ID
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

