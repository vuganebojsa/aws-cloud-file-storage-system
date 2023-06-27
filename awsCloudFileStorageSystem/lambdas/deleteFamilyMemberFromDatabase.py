from .responses import *
import boto3


def delete_family_member_from_database(event, context):
    info = event

    if info is None:
        return get_return('Failed to register user. Missing body.', 400)
    
    inviter_email = info['inviter_email']
    family_email = info['family_email']

    if inviter_email is None or family_email is None:
        return get_return('Failed to confirm registration for user, invalid params', 400)
    
    usr = get_user_by_email(family_email)
    if usr is None:
        return get_return('Invalid email address for family member', 400)

    print(usr)
    user_username = usr['Username']

    dynamodb = boto3.client('dynamodb')
    resp = dynamodb.get_item(
            TableName='invite-bivuja-table',
            Key={
                'id': {'S': inviter_email + '/' + family_email}
            }
        )
    if 'Item' not in resp:
        return get_return('Invalid email address. Please try again', 400)
    
    cognito_client = boto3.client('cognito-idp')
    dynamodb.delete_item(
        TableName='invite-bivuja-table',
        Key={
            'id': {'S': inviter_email + '/' + family_email},
        }
        )
    try:
        resp = cognito_client.admin_delete_user(
            UserPoolId='eu-central-1_JywQCrS95',
            Username=user_username
        )
        return get_return('Succesfully deleted previously created family member.', 200)
    except Exception as e:
        print(e)
        return get_return('Couldnt delete user from user pool.', 400)
     

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
    return users[0]
