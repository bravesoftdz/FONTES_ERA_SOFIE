"""
Your module description
"""

from dateutil.parser import parse

import boto3


def report_statement(**kwargs) -> tuple:
    """
    
    """
    fields = [
        'sofier',
        'task_id',
        'execution_id',
        'operação',
        'data',
        'fase',
        'EM ANÁLISE',
        'APROVADO',
        'DISPONÍVEL',
        'REPROVADO'
    ]
    
    table = boto3.resource('dynamodb').Table('table_sofier_ledger')
    params = dict(
        ProjectionExpression='sofier, task_id, execution_id, first_move, last_move, phase, reward',
        KeyConditionExpression='sofier = :s', 
        ExpressionAttributeValues={':s': kwargs.get('sofier')}
    )
    
    column_name = {
        'VALIDATION': 'EM ANÁLISE',
        'BLOCKED': 'APROVADO',
        'AVAILABLE': 'DISPONÍVEL',
        'WRONG': 'REPROVADO'
    }
    
    buffer = list()
    while True:
        response = table.query(**params)
        
        for each in response.get('Items'):
            buffer.append({
                'sofier': each['sofier'],
                'task_id': each.get('task_id', '-'),
                'execution_id': each.get('execution_id', '-'),
                'operação': 'CRÉDITO' if each['reward'] > 0 else 'DÉBITO',
                'data': (each['first_move'] if each['reward'] > 0 else each['last_move']),
                'fase': each['phase'],
                column_name.get(each['phase']): each['reward'] 
            })
        
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key
        
    buffer = sorted(buffer, key=lambda x: x['data'])
    
    for each in buffer:
        each['data'] = parse(each['data']).strftime('%d/%m/%Y %H:%M')

    return fields, buffer