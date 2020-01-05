"""

"""

import boto3
from boto3.dynamodb.conditions import Key, Attr


def get_statement(sofier: str, phase: str) -> dict:
    """
    
    """
    params = dict(
        FilterExpression=Key('sofier').eq(sofier) & Attr('phase').eq(phase),
    	ProjectionExpression='task_id, execution_id, account, reward, first_move, last_move, sofie_place, task_info, comments, date_to_available '
    )    
    
    table = boto3.resource('dynamodb').Table('table_sofier_ledger')
    
    list_result = list()
    while True:
        response = table.scan(**params)

        for each in response['Items']:
            if each['reward'] >= 0:
                event = {
                    'phase': phase,
                    'task_id': each['task_id'], 
                    'execution_id': each['execution_id'],
                    'reward': each['reward'],
                    'sofie_place': {
                        'name': each['sofie_place']['name'],
                        'address': each['sofie_place'].get('address', ''),
                    },
                    'first_move':  each['first_move'],
                    'last_move': each['last_move'],
                    'date_to_available': each.get('date_to_available', ''),
                    'task': {
                        'type': each['task_info']['type'],
                        'name': each['task_info']['name'],
                        'category': each['task_info']['category']
                    }
                }
                
            else:
                event = {
                    'phase': phase,
                    'reward': each['reward'],
                    'first_move':  each.get('first_move', None) or each['last_move'],
                    'last_move': each['last_move'],
                    'comments': each['comments']
                }

            list_result.append(event)
        
        
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key
        
    return {'data': sorted(list_result, key=lambda x: x['last_move'], reverse=True)}
        
    