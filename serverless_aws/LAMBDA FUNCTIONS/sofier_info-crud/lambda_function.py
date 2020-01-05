import json
import decimal

from sofier_crud import SofierCRUD

def lambda_handler(event, context):
    """
    
    """
    try:
        status = 200
        sofier = None
        
        pathParameters = event['pathParameters']
        if pathParameters:
            sofier = pathParameters.get('sofier')
        
        verb = event['httpMethod']
        
        crud = SofierCRUD()
        
        if verb == 'POST':
            data = json.loads(event['body'], parse_float=decimal.Decimal)
            b_ret = crud.put_info(data)
            data_resp = {'SUCCESS': b_ret}
            status = 200 if b_ret else 500 
            
        elif verb == 'GET':
            if sofier:
                data_resp = crud.get_info(sofier)
            else:
                data_resp = crud.listing()
                
            status = 200 if data_resp else 404
        
        else:
            status, data_resp = 400, {'SUCCESS': False, 'reason': f'Método HTTP não suportado: [{verb}]'}
    except Exception as err:
        status, data_resp = 500, {'SUCCESS': False, 'reason': str(err)}

    return {
        'statusCode': status,
        'body': json.dumps(data_resp),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }        
    }
