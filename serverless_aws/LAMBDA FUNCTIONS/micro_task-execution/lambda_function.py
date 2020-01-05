"""
Esta folha tem dois propósitos:

    1) Listagem de execuções de uma micro tarefa
    2) Um item específico de execução
"""

import json
import boto3
import decimal
from boto3.dynamodb.conditions import Key


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)

        return super(DecimalEncoder, self).default(o)
        

def lambda_handler(event, context):
    """
    
    """
    task_id = event['pathParameters'].get('task_id')
    execution_id = event['pathParameters'].get('execution_id')
    
    if execution_id:
        data = get_execution_item(task_id, execution_id)
        status = 200
    else:
        data = get_execution_list(task_id)
        status = 200 if data else 404
    
    return {
        'statusCode': status,
        'body': json.dumps(data, cls=DecimalEncoder),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }           
    }


def get_execution_list(task_id: str):
    """
    
    """
    table = boto3.resource('dynamodb').Table('table_micro_task_execution')

    scan_params = dict(
        FilterExpression=Key('task_id').eq(task_id),
        ProjectionExpression='task_id, execution_id, who, #when, #result',
        ExpressionAttributeNames={'#when': 'when', '#result': 'result'}
    )
    
    list_final = list()
    while True:
        response = table.scan(**scan_params)
        
        list_final.extend(response['Items'])
        
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        
        scan_params['ExclusiveStartKey'] = last_key
            
    
    return {'data': sorted(list_final, key=lambda x: x['when']['finish'])}
    
    
def get_execution_item(task_id: str, execution_id: str):
    """
    
    """
    table = boto3.resource('dynamodb').Table('table_micro_task_execution')
    
    response = table.get_item(
        Key={'task_id': task_id, 'execution_id': execution_id}
    )
    
    item = response.get('Item')
    if item:
        item['execution'] = sorted(item['execution'], key=lambda x: x.get('when', 'Z'))
    
    return item
    
    