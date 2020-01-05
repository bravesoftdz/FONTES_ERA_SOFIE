import json
import boto3
from collections import defaultdict
from botocore.vendored import requests as requests

def lambda_handler(event, context):
    
    data = get_dashboard()
    
    return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }            
    }


def get_dashboard():
    """
    
    """
    URL = 'https://mysofie.com/api/v2/micro_task/dashboard/'
    HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}
    
    scan_params = dict(
        ProjectionExpression='#status.#state, #status.#status',
        ExpressionAttributeNames={'#state': 'state', '#status': 'status'},
    )
    
    final_state = defaultdict(lambda : 0)
    final_status = defaultdict(lambda : 0)
    
    table = boto3.resource('dynamodb').Table('table_micro_task_in_person')

    while True:
        response = table.scan(**scan_params)
        
        for each in response['Items']:
            final_state[each['status']['state']] += 1
            final_status[each['status']['status']] += 1
        
        last_key_value = response.get('LastEvaluatedKey') 
        if not last_key_value:
            break
            
        scan_params['ExclusiveStartKey'] = last_key_value
        
    response = requests.get(URL, headers=HEADERS)
        
    return {'state': final_state, 'status': final_status, 'life': response.json()}