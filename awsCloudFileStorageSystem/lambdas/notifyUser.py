import json
import boto3


def notify(event, context):
    print(event)
    info_dict = json.loads(event['Records'][0]['Sns']['Message'])
    client = boto3.client('ses', region_name='eu-central-1')  

    try:
        response = client.send_email(
            Source='nebojsavuga@gmail.com',  # Replace with your verified sender email
            Destination={'ToAddresses': [info_dict['receiver']]},
            Message={
                'Subject': {'Data': info_dict['subject']},
                'Body': {'Text': {'Data': info_dict['content']}}
            }
        )
    except Exception as e:
        print(e)

