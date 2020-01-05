# coding: utf-8

"""
Mecanismo por processar, continuamente, os micro contratos,

Basicamente é consumida fila `queue_PROCESS_MICRO_CONTRACT` do Cortex (RabbitMQ)
"""

from datetime import datetime
from json import loads
from threading import Thread, Event

from pika import BasicProperties

from library.common.exception import exception2dict
from library.common.miscellaneous import to_json
from library.storage.cortex import create_new_connection
from library.storage.session import SessionStorage
from micro_contract.micro_contract_base import MicroContractBase
from micro_contract.transaction import Transaction


class MicroContractExecutor(Thread):
    """
    Thread responsável por processar o andamento dos micro contratos
    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        self.__event = Event()
        super().__init__()

    def process_feedback_consumer(self, transaction: str, nps: int, comment: str or None) -> dict:
        """

        :param transaction:
        :param nps:
        :param comment:
        :return:
        """
        assert 1 <= nps <= 5, 'NPS deve ser de 1 à 5'

        obj_transaction = Transaction(transaction)
        obj_transaction.feedback_consumer.when = datetime.utcnow()
        obj_transaction.feedback_consumer.nps = nps
        obj_transaction.feedback_consumer.comment = comment
        obj_transaction.save_soul()

        return {'success': True}

    def process_create(self, sofier: str, card: str, **kwargs) -> dict:
        """
        Cria uma nova transação

        :param sofier:
            Código do Sofier
        :param card:
            Código do Card
        :param kwargs:
            Diversos
        :return:
            Código da transação
        """
        # TODO: À partir do *Card*, localizar e compilar o *Micro Contrato* em questão
        micro_contract = MicroContractBase

        contract = micro_contract(None)
        contract.transaction.sofier = sofier
        contract.transaction.card = card
        contract.transaction.geo.soul = kwargs['body'].get('geo', dict())
        contract.transaction.soul['creation_origin'] = kwargs['body'].get('creation_origin'), list(),
        contract.transaction.save_soul()

        return {
            'transaction': contract.transaction.transaction,
            'data_collect_flow': contract.transaction.card.data_collect_flow.copy()
        }

    def process_run(self, transaction: str, clause: str, **kwargs):
        """
        Dá andamento a uma transação

        :param transaction:
            ID da Transação
        :param clause:
            Nome da cláusula do contrato
        :return:
            O mesmo retorno da execução da cláusula
        """
        buffer = None

        # TODO: À partir da *Transação*, localizar e compilar o *Micro Contrato* em questão
        micro_contract = MicroContractBase

        contract = micro_contract(transaction)

        clause_func = getattr(contract, 'clause_{}'.format(clause))
        if clause_func:
            buffer = clause_func(**kwargs)
        else:
            pass

        contract.transaction.save_soul()

        return buffer

    def process_status(self, transaction: str):
        """

        :param transaction:
        :return:
        """
        obj_transaction = Transaction(transaction)

        if obj_transaction.status.status == 'DATA_COLLECT':  #: Está na fase de coleta de dados
            if obj_transaction.status.soul['processing_stages']['stage_1']:  #: E o link de pagamento foi enviado
                if not obj_transaction.status.soul['processing_stages']['stage_3']:  #: Mas ainda não foi aberto
                    if not SessionStorage().storage.exists(f'MYSOFIE:TRANSACTION:{transaction}:PAYLINK#'):  #: E o link de pagamento expirou
                        obj_transaction.status.status = 'FINISHED'
                        obj_transaction.status.success = False
                        obj_transaction.status.reason = 'PAYMENTLINKEXPIRED'
                        obj_transaction.save_soul()

        return obj_transaction.status.soul

    def process_cancel(self, transaction: str):
        """

        :param transaction:
        :return:
        """
        # TODO: À partir da *Transação*, localizar e compilar o *Micro Contrato* em questão
        micro_contract = MicroContractBase

        contract = micro_contract(transaction)
        contract.cancel()

    def callback(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('ENTROU -> {}'.format(method.routing_key))

        try:
            buffer = None
            routing_parts = method.routing_key.split('.')
            action = routing_parts[-1]

            if action == 'CREATE':
                buffer = self.process_create(**loads(body))

            elif action == 'RUN':
                transaction = routing_parts[-3]
                clause = routing_parts[-2]
                buffer = self.process_run(transaction, clause, **loads(body) if body else dict())

            elif action == 'STATUS':
                transaction = routing_parts[-2]
                buffer = self.process_status(transaction)

            elif action == 'CANCEL':
                transaction = routing_parts[-2]
                self.process_cancel(transaction)

            elif action == 'FEEDBACK_CONSUMER':
                transaction = routing_parts[-2]
                buffer = self.process_feedback_consumer(transaction, **loads(body))

            else:
                Exception('Ação não suportada: {}'.format(action))

        except Exception as err:
            from library.common.service_main import SERVICE_LOGGER
            SERVICE_LOGGER.exception(err)

            channel.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=BasicProperties(correlation_id=properties.correlation_id),
                body=to_json(exception2dict(err))
            )
        else:
            channel.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=BasicProperties(correlation_id=properties.correlation_id),
                body=to_json(buffer)
            )
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

        SERVICE_LOGGER.info('SAIU -> {}'.format(method.routing_key))

    def run(self):
        """

        :return:
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('MicroContractExecutor em execução!')

        channel = create_new_connection('MICRO CONTRACT').channel()
        channel.basic_consume(self.callback, queue='queue_PROCESS_MICRO_CONTRACT', no_ack=False)
        channel.start_consuming()

        self.__event.wait()

        channel.stop_consuming()

    def stop(self):
        """
        Solicita a finalização da Thread de MicroContract
        """
        self.__event.set()
        self.join()
