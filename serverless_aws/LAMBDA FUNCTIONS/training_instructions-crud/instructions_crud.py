"""

"""

import boto3


class InstructionsCRUD(object):
    """
    
    """
    
    def __init__(self):
        """
        
        """
        super().__init__()
        self.__table = boto3.resource('dynamodb').Table('table_micro_task_flows')
    
    
    def listing(self):
        """
        
        """
        list_instructions = list()
        
        params = dict(
            ProjectionExpression='#name, alias',
            ExpressionAttributeNames={'#name': 'name'},
        )
        while True:
            response = self.__table.scan(**params)
            
            for each in response.get('Items'):
                list_instructions.append(each)
            
            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break
            params['LastEvaluatedKey'] = last_key
            
        
        return {'data': list_instructions}
        
    def item(self, name: str) -> dict:
        """
        
        """
        params = dict(
            Key={'name': name, 'version': 1},
            ProjectionExpression='#name, #type, category, reward, lack_days, description, url_video, url_thumbnails, alias',
            ExpressionAttributeNames={'#name': 'name', '#type': 'type'},
        )
        
        response = self.__table.get_item(**params)
        
        return response.get('Item')