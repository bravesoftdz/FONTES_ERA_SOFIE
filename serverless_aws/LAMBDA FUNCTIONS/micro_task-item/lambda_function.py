import json
import decimal
import boto3


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
            
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    
    task_id = event['pathParameters'].get('task_id')
    status, data = get_micro_task_item(task_id)
    
    return {
        'statusCode': status,
        'body': json.dumps(data, cls=DecimalEncoder),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }    
    }


def get_micro_task_item(task_id: str):
    """
    
    """
    FIELDS = [
        'task_id',
        'company',
        '#status',
        'sofie_place',
        'address',
        'original',
        'audit'
    ]
    
    EXPRESSIONS = {
        '#status': 'status'
    }
    
    response = boto3.resource('dynamodb').Table('table_micro_task_in_person').get_item(
        Key={'task_id': task_id},
        ProjectionExpression=', '.join(FIELDS),
        ExpressionAttributeNames=EXPRESSIONS

    )
    
    return 200, response['Item']