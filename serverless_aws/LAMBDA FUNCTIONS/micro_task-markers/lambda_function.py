import json
import boto3
import decimal


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 != 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    """
    Ponto de entrada do AWS Lambda
    """
    data = get_micro_tasks_in_person_markers()
    
    return {
        'statusCode': 200,
        'body': json.dumps(data, cls=DecimalEncoder),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }          
    }
 

def get_micro_tasks_in_person_markers():
    """
    Varre a tabela de micro tarefas listando todas as tarefas com a seu status
    e geo localização
    """
    def to_dict(item) -> dict:
        """
        
        """
        location = item['sofie_place']['location']
        
        return {
            'task_id': item['task_id'],
            'state': item['status']['state'],
            'status': item['status']['status'],
            'name': item['sofie_place']['name'],
            'address': item['address']['formatted_address'],
            'point': {
                'lat': location['lat'],
                'lng': location['lng']
            }
        }
        
    FIELDS = [
        'task_id',
        'sofie_place.#name',
        'address.formatted_address',
        'sofie_place.#location',
        '#status.#state',
        '#status.#status'
    ]
    
    EXPRESSIONS = {
        '#location': 'location', 
        '#status': 'status', 
        '#state': 'state',
        '#name': 'name'
    }
    
    scan_params = dict(
        ProjectionExpression=', '.join(FIELDS),
        ExpressionAttributeNames=EXPRESSIONS,
    )

    table = boto3.resource('dynamodb').Table('table_micro_task_in_person')
    
    list_final = list()
    while True:
        response = table.scan(**scan_params)
        list_final.extend([to_dict(each) for each in response['Items']])
        
        last_key_value = response.get('LastEvaluatedKey') 
        if last_key_value:
            scan_params['ExclusiveStartKey'] = last_key_value
        else:
            break
            

    return {'markers': list_final}