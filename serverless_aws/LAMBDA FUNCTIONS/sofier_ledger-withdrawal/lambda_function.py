import json

from withdrawal import Withdrawal

def lambda_handler(event, context):
    status, data = 200, None
    
    try:
        sofier = event['pathParameters']['sofier']
        phase = event['pathParameters']['phase']
        value = event['queryStringParameters']['value']
        reason = event['queryStringParameters']['reason']
        
        if phase != 'AVAILABLE':
            raise Exception(f'Fase não suportada [{phase}]')
        
        data = Withdrawal(sofier, phase, float(value), reason)()
    except Exception as err:
        status = 500
        data = {'error': str(err)}

    return {
        'statusCode': status,
        'body': json.dumps(data)
    }
