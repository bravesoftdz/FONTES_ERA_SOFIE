"""
Efetua a auditoria de uma execução de tarefa
"""

from datetime import datetime, timedelta

from botocore.vendored import requests as requests
import boto3


class AuditTask(object):
    """
    Efetua o fluxo de auditoria de uma tarefa, a saber:
    
    [X] - Edita o registro da execução da tarefa, inserindo as informações referente à auditoria
    
    [X] - Se APROVADO, passa a tarefa de `state.state` de *NEW* para *FINISHED*
    [X] - Se APROVADO, passa a tarefa de `state.status` de *SUCCESS* para *FAILURE*

    [x] - Se REPROVADO, a tarefa é liberada para um próximo _sofier_

    [x] - Se APROVADO, passa o prêmio do _sofier_ de *VALIDATION* para *BLOCKED*, senão passa para WRONG
    """

    def __init__(self, task_id: str, execution_id: str, who: str, approved: bool, reason: str):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__task_id = task_id
        self.__execution_id = execution_id
        self.__who = who
        self.__approved = approved
        self.__reason = reason
        self.__sofier = None

    def __call__(self):
        """
        Execução propriamente dita
        """
        self.edit_execution()
        self.edit_task()
        self.return_task()
        self.sofier_reward()
        
        return True

    def edit_execution(self):
        """
        Edita a tabela de execução, inserindo as informações referente à auditoria 
        """
        table = boto3.resource('dynamodb').Table('table_micro_task_execution')

        response = table.update_item(
            Key={
                'task_id': self.__task_id,
                'execution_id': self.__execution_id
            },
            UpdateExpression='SET audit = :a',
            ExpressionAttributeValues= {
                ':a': {
                    'when': datetime.utcnow().isoformat(),
                    'who': self.__who,
                    'approved': self.__approved,
                    'reason': self.__reason or '-'
                }
            },
            ReturnValues='ALL_NEW'
        )

        self.__sofier = response['Attributes']['who']

    def edit_task(self):
        """
        Edita a tabela de backlog, mudando o state/status da tarefa
        """
        table = boto3.resource('dynamodb').Table('table_micro_task_in_person')

        response = table.update_item(
            Key={'task_id': self.__task_id},
            UpdateExpression='SET #status.#state = :state, #status.#status = :status',
            ExpressionAttributeNames={'#status': 'status', '#state': 'state'},
            ExpressionAttributeValues= {
                ':state': 'FINISHED',
                ':status': 'SUCCESS' if self.__approved else 'FAILURE'
            }
        )

    def return_task(self):
        """
        Caso a execução da tarefa seja reprovada pela auditoria, a mesma é liberada para o próximo sofier
        """
        if not self.__approved:
            table = boto3.resource('dynamodb').Table('table_micro_task_in_person')

            response = table.get_item(
                Key={'task_id': self.__task_id},
            )

            data = response['Item']

            data = {
                'category': data['task']['category'],
                'type': data['task']['type'],
                'task_id': data['task_id'],
                'reward': float(data['task']['reward']),
                'csv_row': int(data['status']['row_line']), 
                'name': data['sofie_place']['name'],
                'address': data['address']['formatted_address'],
                'lat': float(data['google_maps']['results'][0]['geometry']['location']['lat']),
                'lng': float(data['google_maps']['results'][0]['geometry']['location']['lng'])
            }

            response = requests.post(
                'https://mysofie.com/api/v2/micro_task/', 
                headers={'Authorization': 'Bearer RVVfU09VX0FfTEVOREE='},
                json=data
            )

    def sofier_reward(self):
        """
        Movimenta o *prêmio* do _sofier_ de acordo com a aprovação, ou reprovação, da execução da tarefa
        """
        phase = 'BLOCKED' if self.__approved else 'WRONG'
        dt_when = datetime.utcnow().isoformat()
        date_to_available = (datetime.utcnow() + timedelta(days=30)).isoformat()

        table = boto3.resource('dynamodb').Table('table_sofier_ledger')

        table.update_item(
            Key={
                'sofier': self.__sofier,
                'execution_id': self.__execution_id
            },
            UpdateExpression='SET phase = :p, last_move = :m, history = list_append(history, :h), date_to_available = :a',
            ExpressionAttributeValues= {
                ':p': phase,
                ':m': dt_when,
                ':h': [{'phase': phase, 'time_stamp': dt_when}],
                ':a': date_to_available
            }
        )
