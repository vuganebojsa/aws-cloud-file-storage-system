import json
from .responses import *
import boto3
import base64
import uuid

def share_file(giver, receiver, path):

    dynamodb_client = boto3.client('dynamodb')
    #body
    # who is sharing,
    #  what is sharing?(path, if doesnt contain . its a folder, if it contains its a file), 
    # to who is sharing
    # content-share-bivuja-table
    # if shared folder just list the folder content and share it, without other folders, without other folders
    if giver is None or receiver is None or path is None:
        return get_return('Not all parameters were entered.', 400)
    item_id = str(uuid.uuid4())
    try:
        response = dynamodb_client.put_item(
            TableName='content-share-bivuja-table',
            Item={
                'id':{
                    'S': item_id
                },
                'giver':{
                    'S': giver
                },
                'receiver':{
                    'S': receiver
                },
                'path':{
                    'S': path
                }
            }
        )
        return get_return('File shared successfully', 200)
    except Exception as e:
        return get_return('Failed to share data', 400)
    



def query_table_with_multiple_keys(giver):
    table_name = 'bivuja-table'
    dynamodb = boto3.resource('dynamodb')

    # Access the DynamoDB table
    table = dynamodb.Table(table_name)
    response = table.scan(
       FilterExpression='#usr = :giver',
        ExpressionAttributeValues={
            ':giver': giver
        },
        ExpressionAttributeNames={
            '#usr': 'username'
        }
    )

    items = response['Items']
    # Process the items as needed
    return items

def get_all_files(inviter_email):
    user = get_user_by_email(inviter_email)
    if user is None:
        return get_return('Invalid email address for inviter', 400)
    user_username = user['Username']
    items = query_table_with_multiple_keys(user_username)
    filtered_files = []
    if len(items) != 0:
        for item in items:
            filtered_files.append(item)
    
    no_duplicates = []
    for f in filtered_files:
        if f not in no_duplicates:
            no_duplicates.append(f)
    
    return no_duplicates
    
    
def confirm_decline_invitation(event, context):
    info = json.loads(event['body'])

    if info is None:
        return get_return('Failed to register user. Missing body.', 400)
    
    inviter_email = info['inviterEmail']
    family_email = info['familyEmail']
    status = info['status'] # accepted/declined
    # fetch username from users

    if inviter_email is None or family_email is None or status is None:
        return get_return('Failed to confirm registration for user, invalid params', 400)
    
    usr = get_user_by_email(family_email)
    if usr is None:
        return get_return('Invalid email address for family member', 400)

    print(usr)
    user_username = usr['Username']
    giver_usr = get_user_by_email(inviter_email)['Username']


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
    if res['status'] != 'pending':
        return get_return('This request has already been processed.', 400)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('invite-bivuja-table')
    try:
        response = table.update_item(
                Key={'id': inviter_email+'/'+family_email},
                UpdateExpression='SET #tp = :value4',
                ExpressionAttributeValues={
                    ':value4': status
                },
                ExpressionAttributeNames={
                    '#tp': 'status'
                }, 
                ReturnValues='ALL_NEW')
        return get_return('Successfully ' + status + ' the family request', 200)
    except Exception as e:
        print(e)
        return get_return('Key error.', 400)

        #cognito_client = boto3.client('cognito-idp')

        # # promeniti status u tabeli u accepted
        # try:
        #     response = cognito_client.admin_update_user_attributes(
        #         UserPoolId='eu-central-1_JywQCrS95',
        #         Username=user_username,
        #         UserAttributes=[{
        #             'Name':'email_verified',
        #             'Value':'true'
        #         }]
        #     )

        #     all_files = get_all_files(inviter_email)
        #     for f in all_files:
        #         print(f)
        #         if f['folderName'] != '':
        #             share_file(giver_usr, user_username, f['folderName'] + '/' + f['filename'])
        #         else:
        #             share_file(giver_usr, user_username, f['filename'])

        #     dynamodb.delete_item(
        #         TableName='invite-bivuja-table',
        #         Key={
        #             'id': {'S': inviter_email + '/' + family_email},
        #         }
        #      )

        #     send_email(family_email, inviter_email + ' has confirmed your account', inviter_email + ' has confirmed your account. You may acces all their files!')

        #     return get_return('Successfully accepted registraion of a family member.', 200)
        # except Exception as e:
        #     print(e)
        #     return get_return('Invalid username. ', 400)

        # promeniti status u tabeli u declined
        # obrisati iz user poola


        # try:
        #     resp = cognito_client.admin_delete_user(
        #         UserPoolId='eu-central-1_JywQCrS95',
        #         Username=user_username
        #     )

        #     dynamodb.delete_item(
        #         TableName='invite-bivuja-table',
        #         Key={
        #             'id': {'S': inviter_email + '/' + family_email},
        #         }
        #     )

        #     return get_return('The request has been declined. User not registered.', 200)

        # except Exception as e:
        #     print(e)
        #     return get_return('Couldnt delete user from user pool.', 400)
  



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
    return users[0]


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
    return users[0]
