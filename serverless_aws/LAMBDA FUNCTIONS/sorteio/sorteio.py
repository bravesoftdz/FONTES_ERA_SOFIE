import random

import boto3

def sorteio(when: str or None) -> tuple:
    """
    
    """
    
    table = boto3.resource('dynamodb').Table('table_sofier_info')
    
    FINAL_LIST = list()
    
    params = dict(
        ProjectionExpression='short_name, sofier, #when',
        ExpressionAttributeNames={'#when': 'when'},
    )
    while True:
        response = table.scan(**params)
        
        for each in response.get('Items'):
            if when:
                if each['when'][:10] != when:
                    continue
                
            FINAL_LIST.append((each['short_name'], each['sofier']))
        
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break
        params['LastEvaluatedKey'] = last_key
        
    print(FINAL_LIST)    
        
    return FINAL_LIST[random.randrange(len(FINAL_LIST))]    
    