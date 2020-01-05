"""
Módulo responsável por calcular os saldo do _sofier_

A versão atual varre a tabela do DynamoDB até que seja possível utilizar o Redis
"""

import boto3
from boto3.dynamodb.conditions import Key


def get_balance(sofier: str) -> dict:
    """
    Rotina responsável por consolidar o saldo de um _sofier_
    """
    params = dict(
        KeyConditionExpression=Key('sofier').eq(sofier),
        ProjectionExpression='phase, reward'
    )
    
    table = boto3.resource('dynamodb').Table('table_sofier_ledger')
    
    dict_result = {key: 0 for key in ('VALIDATION', 'BLOCKED', 'AVAILABLE', 'WRONG')}
    has_available_movement = False
    
    while True:
        response = table.query(**params)
        
        for each in response['Items']:
            dict_result[each['phase']] += each['reward']

            if each['phase'] == 'AVAILABLE':
                has_available_movement = True    
        
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key

    dict_result['has_available_movement'] = has_available_movement
        
    return dict_result