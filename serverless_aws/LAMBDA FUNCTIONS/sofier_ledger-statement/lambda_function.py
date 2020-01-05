import json
import ledger

import decimal

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
            
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    
    sofier = event['pathParameters'].get('sofier')
    phase = event['pathParameters'].get('phase')
    
    data = ledger.get_statement(sofier, phase)
    
    return {
        'statusCode': 200,
        'body': json.dumps(data, cls=DecimalEncoder)
    }
