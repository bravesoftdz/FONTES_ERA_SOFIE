import json

from support import TicketFlow


def lambda_handler(event, context):
    """
    
    """
    step = 'Iniciando'
    data = None
    status = 200
    try:
        ticket = TicketFlow()
        
        if event['httpMethod'] == 'GET':
            step = 'GET'
            sofier = event['pathParameters'].get('sofier')
            data = ticket.listing_by_sofier(sofier)
            status = 200
        
        elif event['httpMethod'] == 'POST':
            step = 'POST'
            content = json.loads(event['body'])
            data = ticket.open_new_ticket(content)
            status = 201
        
        elif event['httpMethod'] == 'PUT':
            step = 'PUT'
            content = json.loads(event['body'])

            if content['status'] == 'IN_PROGRESS':
                sofier = event['pathParameters']['sofier']
                ticket_id = event['pathParameters']['ticket_id']
                
                data = ticket.set_in_progress(sofier, ticket_id, content['who'])
                
            elif content['status'] == 'FINISHED':
                sofier = event['pathParameters']['sofier']
                ticket_id = event['pathParameters']['ticket_id']
                
                data = ticket.set_finished(sofier, ticket_id, content['who'], content['conclusion'])

            else:
                raise Exception(f"Novo status não suportado: [{content['status']}]")
                
            status = 200

    except Exception as err:
        status = 500
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
