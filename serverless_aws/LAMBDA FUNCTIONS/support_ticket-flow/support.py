from uuid import uuid1
from datetime import datetime

import boto3


class TicketFlow(object):
    """
    
    """
    
    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__table = boto3.resource('dynamodb').Table('table_support_ticket')
        
    def open_new_ticket(self, content: dict) -> str:
        """
        Abre um novo ticket
        """
        ticket_id = str(uuid1())

        content['ticket_id'] = ticket_id
        content['when'] = datetime.utcnow().isoformat()
        content['status'] = 'NEW'
        self.__table.put_item(Item=content)
        
        return {'ticket_id': ticket_id}
        
    def listing_by_sofier(self, sofier: str) -> list:
        """
        Listagem de tickets por sofier
        """
        params = dict(
            KeyConditionExpression='sofier = :s',
            ExpressionAttributeValues={':s': sofier}            
        )
        
        response = self.__table.query(**params)
        
        return {'data': sorted([each for each in response.get('Items')], key=lambda x: x['when'], reverse=True)}
        
    def set_in_progress(self, sofier: str, ticket_id: str, who: str) -> bool:
        """
         
        :param who:
            ID do profissional que tratará o ticket
        """
        self.__table.update_item(
            Key={'sofier': sofier, 'ticket_id': ticket_id},
            UpdateExpression='set #status = :status, backoffice = :bko',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'IN_PROGRESS', ':bko': {'who': who, 'when': datetime.utcnow().isoformat()}}
        )
        
        return True
        
    def set_finished(self, sofier: str, ticket_id: str, who: str, conclusion: str) -> bool:
        """
        
        """
        self.__table.update_item(
            Key={'sofier': sofier, 'ticket_id': ticket_id},
            UpdateExpression='set #status = :status, conclusion = :conclusion',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'FINISHED',
                ':conclusion': {
                    'who': who, 
                    'when': datetime.utcnow().isoformat(),
                    'content': conclusion
                }
            }
        )
        
        return True
        