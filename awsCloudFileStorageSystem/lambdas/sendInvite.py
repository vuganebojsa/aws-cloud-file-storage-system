import json
from .responses import *
import boto3

def send_invite(event, context):

    dynamodb_client = boto3.client('dynamodb')
    info = event['body']

    info_dict = json.loads(info)
    if info_dict.get('inviter') == info_dict.get('familyMember'):
        return {
            'statusCode': 400,
            'body':'You cant invite yourself.'
        }
    if info_dict.get('inviter') is None or info_dict.get('familyMember') is None:
        return {
            'statusCode': 400,
            'body':'Not all parameters were entered.'
        }
    dynamodb = boto3.client('dynamodb')

    resp = dynamodb.get_item(
            TableName='invite-table-bivuja',
            Key={
                'id': {'S': info_dict['inviter'] + '/' + info_dict['familyMember']}
            }
        )
    # Check if the record exists
    if 'Item' in resp:
        return {
            'statusCode': 400,
            'body':'Already invited family member.'
        }
    
    
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
        return {
            'statusCode': 200,
            'body': 'Data shared successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Failed to share data: {str(e)}'
        }