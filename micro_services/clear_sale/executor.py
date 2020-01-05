# coding: utf-8

"""

"""

from threading import Thread, Event

from pika import BasicProperties

from library.common.exception import exception2dict
from library.common.miscellaneous import to_json
from library.storage.cortex import create_new_connection
from micro_contract.transaction import Transaction
from the_3rd.clear_sale.trust import ClearSaleTrust, ClearSaleAuth


class ClearSaleExecutor(Thread):
    """

    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__event = Event()
        self.__clear_sale_auth = ClearSaleAuth()
        self.__token = None

    def __process_analysis(self, transaction: str):
        """

        :param transaction:
        :return:
        """
        transaction_obj = Transaction(transaction)

        trust = ClearSaleTrust()
        buffer = trust(
            token=self.__clear_sale_auth.token,
            document=transaction_obj.consumer.consumer,
            document_type='CPF',
            phone=transaction_obj.consumer.phone,
            zip_code=transaction_obj.address.zipcode,
            email=transaction_obj.consumer.email,
            transaction=transaction_obj.transaction,
            description=transaction_obj.card.title,
            price=transaction_obj.payment_condition.price,
            consumer=transaction_obj.consumer.full_name
        )

        return buffer

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
            transaction = method.routing_key.split('.')[-1]
            buffer = self.__process_analysis(transaction)
        except Exception as err:
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
        Mantêm o Thread em execução
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('ClearSaleExecutor em execução!')

        channel = create_new_connection('CLEAR SALE').channel()
        channel.basic_consume(self.callback, queue='queue_PROCESS_FRAUD_CLEARSALE', no_ack=False)
        channel.start_consuming()

        self.__event.wait()

        channel.stop_consuming()

    def stop(self):
        """
        Solicita a finalização da Thread de ClearSaleExecutor
        """
        self.__event.set()
        self.join()
