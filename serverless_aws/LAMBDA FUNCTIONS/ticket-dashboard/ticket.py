import boto3

class TicketManagement(object):
    """
     
    """
    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__table = boto3.resource('dynamodb').Table('table_support_ticket') 
    
    def dashboard(self):
        """
        Oferece um resumo das quantidades de tickets e seus status
        """
        params = dict(
            ProjectionExpression='#status',
            ExpressionAttributeNames={'#status': 'status'}
        )
        
        buffer = {k: 0 for k in ('NEW', 'IN_PROGRESS', 'FINISHED')}
        
        while True:
            response = self.__table.scan(**params)
            
            for each in response.get('Items'):
                buffer[each['status']] += 1
                
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            params['ExclusiveStartKey'] = last_key

        return buffer
        
    def listing(self, status: str) -> str:
        """
        Listagem de tickets à partir de um status
        """
        buffer = list()
        params = dict(
            FilterExpression='#status =:status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': status}
        )

        while True:
            response = self.__table.scan(**params)
            
            buffer.extend(response.get('Items'))
            
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            params['ExclusiveStartKey'] = last_key
            
        return {'data': sorted(buffer, key=lambda x: x['when'])}
        