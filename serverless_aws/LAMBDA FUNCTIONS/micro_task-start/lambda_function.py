import json
import boto3
import decimal
from botocore.vendored import requests as requests
from uuid import uuid1


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
            
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    
    task_id = event['pathParameters'].get('task_id')
    sofier = event['queryStringParameters'].get('sofier')
    
    status, data = set_start_execution(task_id, sofier)
    
    return {
        'statusCode': status,
        'body': json.dumps(data, cls=DecimalEncoder),
        'headers': {
            'Access-Control-Allow-Origin': '*'    
        }            
    }

URL = 'https://mysofie.com/api/v2/micro_task/execution/{task_id}/start'

HEADERS = {'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='}

def set_start_execution(task_id: str, sofier: str) -> tuple:
    """
    
    [X] - Recupera o nome da tarefa atrelada à tarefa
    [X] - Recupera o fluxo de execução da tarefa
    [X] - Sinaliza à Bússola o status da tarefa
    """
    status, buffer = 500, None

    #: MARCA NA TABELA DE TAREFAS QUE A TAREFA ESTÁ EM EXECUÇÃO, RECUPERANDO AS VARIABLES
    response_task = boto3.resource('dynamodb').Table('table_micro_task_in_person').get_item(
        Key={'task_id': task_id},
        ProjectionExpression='task.#name, variables',
        ExpressionAttributeNames={'#name': 'name'}
    )

    #: RECUPERA O FLUXO DE EXECUÇÃO DA TAREFA
    response_flow = boto3.resource('dynamodb').Table('table_micro_task_flows').get_item(
        Key={'name': response_task['Item']['task']['name'], 'version': 1}
    )

    #: SINALIZA AO BACKEND LEGADO DE QUE A TAREFA FOI INICIADA
    response = requests.post(URL.format(task_id=task_id), headers=HEADERS, params={'sofier': sofier})
    if response.status_code != 200:
        return response.status_code, response.json()

    #: Formatando a resposta final
    status = 200
    response = {
        'task_id': task_id,
        'execution_id': str(uuid1()),
        'task_flow': response_flow['Item']['task_flow'],
        'variables': response_task['Item'].get('variables', dict()),
        'task_info': {
            'name': response_flow['Item']['name'],
            'version': response_flow['Item']['version']
        }
    }
    
    return status, response