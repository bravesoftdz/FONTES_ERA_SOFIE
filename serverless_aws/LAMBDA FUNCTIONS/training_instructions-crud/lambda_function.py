import json
import decimal

from instructions_crud import InstructionsCRUD


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
            
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    status = 200
    try:
        parameters = event.get('pathParameters') or dict()
        
        if 'name' in parameters:
            data = InstructionsCRUD().item(parameters['name'])
            if not data:
                status = 404
        else:
            data = InstructionsCRUD().listing()

        # print(data)
    except Exception as err:
        status = 500
        data = {'err': str(err)}
    
    return {
        'statusCode': status,
        'body': json.dumps(data, cls=DecimalEncoder)
    }
