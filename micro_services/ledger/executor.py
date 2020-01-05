# coding: utf-8

"""

"""

from datetime import datetime, timedelta
from json import loads
from threading import Thread, Event
from uuid import uuid4
from locale import currency

from pika import BasicProperties

from crud.ledger import LedgerCRUD
from library.common.exception import exception2dict
from library.common.governance import DEVELOPER_SESSION
from library.common.miscellaneous import to_json
from library.common.paging_info import PagingInfo
from library.storage.cortex import create_new_connection
from micro_contract.actors.sofier import Sofier


class LedgerExecutor(Thread):
    """
    Responsável por lidar com o "Livro Razão" e as "Carteiras" das partes envolvidas
    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__event = Event()
        self.__ledger_crud = LedgerCRUD(PagingInfo(fields=['type', 'transaction', 'value', 'description', '__created__.when']), DEVELOPER_SESSION)

    def process_entry(self, part_type: str, part_id: str, transaction: str or None, value: float, description: str, type_entry: str = 'Cr'):
        """
        Cria uma nova entrada no Livro Razão

        :param part_type:
            Tipo da parte envolvida: sofier, company, platform
        :param part_id:
            ID da parte
        :param transaction:
            Referência à transação, quando pertinente
        :param value:
            Valor sendo movimentado
        :param description:
            Descrição da operação
        :param type_entry:
            Tipo de movimentação: Cr - Crédito, Dr - Débito
        :return:
            Dicionário com o código da movimentação
        """
        entry = str(uuid4())

        data = {
            'name': entry,
            'part': {
                'type': part_type,
                'id': part_id,
            },
            'type': type_entry,
            'transaction': transaction,
            'value': value,
            'description': description
        }

        self.__ledger_crud.create(entry, data)

        return {'entry': entry}

    def process_balance(self, part_type: str, part_id: str) -> dict:
        """
        Calcula o balanço, saldo e movimentação, de uma determinada parte

        :param part_type:
            Tipo da parte envolvida: sofier, company, platform
        :param part_id:
            ID da parte
        :return:
        """
        return self.__ledger_crud.balance(part_type, part_id)

    def process_rescue(self, part_type: str, part_id: str) -> dict:
        """

        :return:
        """
        sofier = Sofier(part_id)

        sofier.bank_checking_account.check()

        balance = self.process_balance(part_type, part_id)
        final_balance = balance['balance']['final_balance']

        if final_balance < 10:
            raise Exception(f'Saldo insuficiente para resgate: {currency(final_balance, grouping=True)}')

        to_date: str = (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y')

        self.process_entry(
            part_type=part_type,
            part_id=part_id,
            transaction=None,
            value=final_balance,
            description='Resgate solicitado - Previsto para {}'.format(to_date),
            type_entry='Dr'
        )

        return {
            'part': {
                'type': part_type,
                'id': part_id
            },
            'value': final_balance
        }

    def callback(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        utc_init = datetime.utcnow()

        try:
            buffer = None
            routing_parts = method.routing_key.split('.')
            action = routing_parts[-1]

            if action == 'ENTRY':
                buffer = self.process_entry(**loads(body))

            elif action == 'BALANCE':
                buffer = self.process_balance(**loads(body))

            elif action == 'RESCUE':
                buffer = self.process_rescue(**loads(body))

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

            from library.common.service_main import SERVICE_LOGGER
            elapsed = round((datetime.utcnow() - utc_init).total_seconds() * 1000)
            SERVICE_LOGGER.info('{} MILISSEGUNDOS - {}'.format(elapsed, method.routing_key))

    def run(self):
        """

        :return:
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('LedgerExecutor em execução!')

        channel = create_new_connection('LEDGER').channel()
        channel.basic_consume(self.callback, queue='queue_PROCESS_LEDGER', no_ack=False)
        channel.start_consuming()

        self.__event.wait()

        channel.stop_consuming()

    def stop(self):
        """
        Solicita a finalização da Thread de MicroContract
        """
        self.__event.set()
        self.join()
