import json
from botocore.vendored import requests as requests

URL = 'https://mysofie.com/api/v2/micro_task/reserve/'

HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}

def lambda_handler(event, context):
    
    params = event.get('queryStringParameters', dict())
    
    status, data = get_reserveds(**params)
    
    return {
        'statusCode': status,
        'body': json.dumps(data)
    }


def get_reserveds(**kwargs) -> tuple:
    """
    
    """
    status, buffer = 500, None
    
    response = requests.get(URL, headers=HEADERS, params=kwargs)
    
    buffer = response.json().copy() 
    
    for each in buffer['data']:
        each['task_name'] = 'PAT'
    
    return response.status_code, buffer