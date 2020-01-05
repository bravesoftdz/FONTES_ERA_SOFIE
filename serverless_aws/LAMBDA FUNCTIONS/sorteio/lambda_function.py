import json

from sorteio import sorteio


def lambda_handler(event, context):
    
    when = None
    
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters:
        when = queryStringParameters.get('when_start')

    sofier, email = sorteio(when)

    return {
        'statusCode': 200,
        'body': json.dumps({'sofier': sofier, 'email': email}),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }        
    }
