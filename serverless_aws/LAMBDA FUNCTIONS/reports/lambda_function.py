import json
import decimal

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
            
        return super(DecimalEncoder, self).default(o)



def lambda_handler(event, context):
    
    verb = event['httpMethod']
    
    if verb == 'GET':
        from list_report import get_reports
        
        data = get_reports()
        
        return {
            'statusCode': 200,
            'body': json.dumps(data),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    
    elif verb == 'POST':
        rep_name = event['queryStringParameters'].pop('name')
        rep_format = event['queryStringParameters'].pop('format')
        rep_params = event['queryStringParameters']
        
        from build_report import build_report
        data = build_report(rep_name, rep_format, **rep_params)
        
        headers = {'Access-Control-Allow-Origin': '*'}
        
        if rep_format == 'CSV':
            headers['Content-Type'] = 'text/csv'
            headers['Content-Disposition'] = f'attachment; filename={"teste"}.csv'
        elif rep_format == 'JSON':
            data = json.dumps(data, cls=DecimalEncoder)
            headers['Content-Type'] = 'application/json'

        return {
            'statusCode': 200,
            'body': data,
            'headers': headers
        }
