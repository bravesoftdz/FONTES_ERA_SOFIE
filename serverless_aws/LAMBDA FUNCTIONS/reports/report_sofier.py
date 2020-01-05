"""
Your module description
"""

import boto3

def report_sofier(**kwargs) -> tuple:
    """
    
    """
    fields = [
        'sofier',
        'short_name',
        'full_name',
        'document',
        'birthday',
        'when'
    ]
    
    params = dict(
        ProjectionExpression='sofier, short_name, full_name, document, birthday, #when',
        ExpressionAttributeNames={'#when': 'when'},
    )
    table = boto3.resource('dynamodb').Table('table_sofier_info')

    buffer = list()
    while True:
        response = table.scan(**params)
    
        buffer.extend(response.get('Items'))

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['ExclusiveStartKey'] = last_key
    
    return fields, sorted(buffer, key=lambda x: x['when'])