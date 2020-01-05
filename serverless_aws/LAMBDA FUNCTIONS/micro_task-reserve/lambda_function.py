import json
from botocore.vendored import requests as requests

def lambda_handler(event, context):
    
    params = event.get('queryStringParameters', dict())
    
    status, data = get_new_task(**params)
    
    return {
        'statusCode': status,
        'body': json.dumps(data)
    }


URL = 'https://mysofie.com/api/v2/micro_task/reserve/'

HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}


def get_new_task(**kwargs) -> tuple:
    """
    
    """
    status, buffer = 500, None
    response = requests.post(URL, headers=HEADERS, params=kwargs)
    
    if response.status_code == 200:
        status = 200
        buffer = response.json().copy()
        buffer['task_name'] = 'PAT'
        
    elif response.status_code == 204:
        status = 204
        buffer = None
        
    else:
        status = response.status_code
        buffer = response.json()
        
    
    return status, buffer
    
    