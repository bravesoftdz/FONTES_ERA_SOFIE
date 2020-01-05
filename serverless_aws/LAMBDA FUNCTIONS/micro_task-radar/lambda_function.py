import json

from radar import get_radar, register_bread_crumbs


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
            
        return super(DecimalEncoder, self).default(o)
        

def lambda_handler(event, context):
    
    sofier = event['queryStringParameters'].get('sofier')
    lat = event['queryStringParameters'].get('lat')
    lng = event['queryStringParameters'].get('lng')
    radius = event['queryStringParameters'].get('radius')
    
    status, data = get_radar(lat=lat, lng=lng, radius=radius)
    
    register_bread_crumbs(sofier, lat, lng, len(data['data']))

    return {
        'statusCode': status,
        'body': json.dumps(data, cls=DecimalEncoder),
        'headers': {
            'Access-Control-Allow-Origin': '*'    
        }          
    }
