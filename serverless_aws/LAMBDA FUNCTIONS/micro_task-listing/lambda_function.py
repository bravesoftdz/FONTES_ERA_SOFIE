import json
import boto3
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    params = {
        'company': event['queryStringParameters'].pop('company', ''),
        'last_task_id': event['queryStringParameters'].pop('last_task_id', ''),
        'state': event['queryStringParameters'].pop('state', ''),
        'limit': event['queryStringParameters'].pop('limit', 10) or 10,
        'filter': event['queryStringParameters']
    } 
    
    data = get_listing(**params)
    
    return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }         
    }


def get_listing(**kwargs):
    """
    Recupera a listagem de tarefa de acordos com os parâmetros
    """
    list_final = list()
    
    FIELDS = [
        'company',
        'task_id',
        'task.#type',
        'task.category',
        'task.#name',
        '#status.#state',
        '#status.#status',
        '#status.last_sofier',
        'address.city',
        'address.#state',
        'original',
        'last_movement'
    ]
    
    EXPRESSIONS = {
        '#status': 'status', 
        '#state': 'state',
        '#name': 'name',
        '#type': 'type'
    }  
    
    filter_params = kwargs.get('filter', dict())
    filter_string = '';
    filter_values = dict()
    
    scan_params = dict(
        ProjectionExpression=', '.join(FIELDS),
        ExpressionAttributeNames=EXPRESSIONS,
        #: IndexName='task_id-last_movement-index',
        Limit=int(kwargs['limit'])
    )
    
    last_task_id = kwargs.pop('last_task_id', None)
    if last_task_id:
        scan_params['ExclusiveStartKey'] = {'task_id': last_task_id}
        
    if 'state' in kwargs:
        filter_string += '#status.#state = :state'
        filter_values[':state'] = kwargs['state']
        
    if 'status.last_sofier' in filter_params: 
        filter_string += ' and #status.last_sofier = :sofier' if filter_string else '#status.last_sofier = :sofier'
        filter_values[':sofier'] = filter_params['status.last_sofier']

    if filter_string:
        scan_params['FilterExpression'] = filter_string
        scan_params['ExpressionAttributeValues'] = filter_values

    table = boto3.resource('dynamodb').Table('table_micro_task_in_person')

    qtt = 0
    while True:
        response = table.scan(**scan_params)

        for each in response['Items']:
            new_item = {
                'company': each['company'],
                'task_id': each['task_id'], 
                'task': {
                    'type': each['task']['type'],
                    'category': each['task']['category'],
                    'name': each['task']['name'],
                },
                'status': {
                    'state': each['status']['state'],
                    'status': each['status']['status'],
                    'last_sofier': each['status'].get('last_sofier')
                },
                'address': {
                    'city': each['address']['city'],
                    'state': each['address']['state']
                },
                'original': each['original'],
                'last_movement': each['last_movement']
            }
            list_final.append(new_item)

            qtt += 1
            if qtt == scan_params['Limit']:
                break

        if qtt >= scan_params['Limit']:
            break
           
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        scan_params['ExclusiveStartKey'] = last_key

    last_key = response.get('LastEvaluatedKey', dict()).get('task_id')

    return {
        'data': list_final, 
        'last_key': last_key
    }