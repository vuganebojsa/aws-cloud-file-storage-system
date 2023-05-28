import json

def get_200_response(data):
    return {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        'statusCode': 200,
        'body': json.dump(data)
    }
def get_400_response(data):
    return {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        'statusCode': 400,
        'body': json.dump(data)
    }

def get_401_response(data):
    return {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        'statusCode': 401,
        'body': json.dump(data)
    }
def get_404_response(data):
    return {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        'statusCode': 404,
        'body': json.dump(data)
    }
def get_500_response(data):
    return {
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Methods':'*',
            'Access-Control-Allow-Origin':'*'
        },
        'statusCode': 500,
        'body': json.dump(data)
    }