import json

from training_tips_crud import TraningTipsCRUD

def lambda_handler(event, context):
    """
    
    """

    step = 'Iniciando'
    try:
        status, data = 200, None
        crud = TraningTipsCRUD()
        path_parameters = event.get('pathParameters')
        query_parameters = event.get('queryStringParameters')
        
        if event['httpMethod'] == 'GET':
            step = 'ENTROU NO GET'
            content_id = path_parameters.get('content_id') if path_parameters else None
            step = 'PEGOU O `content_id`'
            if not content_id:
                data = crud.listing()
                status = 200
            
            else:
                jump = query_parameters.get('jump') if query_parameters else None
                
                if jump == 'next':
                    data = crud.next_tip(content_id)
                    status = 200 if data else 404
                    
                else:
                    data = crud.item(content_id) 
                    status = 200 if data else 404
            
        elif event['httpMethod'] == 'POST':
            content = json.loads(event['body'])
            data = crud.create_tip(content)
            status = 201
            
        elif event['httpMethod'] == 'PUT':
            content = json.loads(event['body'])
            data = crud.edit_tip(content)
            status = 200
            
        elif event['httpMethod'] == 'DELETE':
            content_id = path_parameters.get('content_id')
            crud.delete_tip(content_id)
            status = 200
            
        else:
            status, data = 400, {'reason': f"Operação não reconhecida: [{event['httpMethod']}]"}
            
    except Exception as err:
        data = {
            'step': step,
            'error': str(err)
        }
    
    
    return {
        'statusCode': status,
        'body': json.dumps(data),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
