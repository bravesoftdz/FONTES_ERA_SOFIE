import json

from ticket import TicketManagement


def lambda_handler(event, context):
    """
    
    """
    status, data = 200, None
    
    ticket = TicketManagement()
   
    try: 
        if event['resource'].lower() == '/ticket/dashboard':
            data = ticket.dashboard()
            
        elif event['resource'].lower() == '/ticket/management':
            ticket_status = event['queryStringParameters'].get('status')
            if not ticket_status:
                status = 400
                data = {'error': 'Não foi definido um status de ticket válido'}
            else:
                data = ticket.listing(ticket_status)
            
    except Exception as err:
        status = 500
        data['error'] = str(err)

    # data['path'] = event['path']
    # data['resource'] = event['resource']

    return {
        'statusCode': status,
        'body': json.dumps(data),
        'headers': {
    	    'Access-Control-Allow-Origin': '*'    
        }       
    }
