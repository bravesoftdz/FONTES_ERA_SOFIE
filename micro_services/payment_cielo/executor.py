# coding: utf-8

from json import loads
from threading import Thread, Event

from pika import BasicProperties

from the_3rd.cielo.payment import query_bin, authorization, capture, cancel
from library.common.exception import exception2dict
from library.common.miscellaneous import to_json
from library.storage.cortex import create_new_connection


class PaymentCieloExecutor(Thread):
    """

    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        super().__init__()
        self.__event = Event()

    def format_value(self, value: float) -> str:
        """

        :param value:
        :return:
        """
        return ''.join('{:.2f}'.format(value).split('.'))

    def __process_authorization(self, transaction: str, number: str, cvv: str, flag: str, expiration: str, holder: str, value: float, installments: int, soft_description: str) -> dict:
        """

        :param transaction:
        :param number:
        :param cvv:
        :param flag:
        :param expiration:
        :param holder:
        :param value:
        :param installments:
        :param soft_description:
        :return:
        """
        return authorization(transaction, number, cvv, flag, expiration, holder, value, installments, soft_description)

    def __process_capture(self, order_id: str):
        """

        :param order_id:
        :param value:
        :return:
        """
        return capture(order_id)

    def __process_cancel(self, order_id: str):
        """

        :param order_id:
        :return:
        """
        return cancel(order_id)

    def __processo_query_bin(self, number: str) -> dict:
        """
        Consulta se um determinado número de cartão é apto a ser utilizado

        :return:
            `dict` com as informações
        """
        return query_bin(number)

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
            parts = method.routing_key.split('.')
            action = parts[-1]
            transaction = parts[-2]

            if action == 'AUTHORIZATION':
                buffer = self.__process_authorization(transaction, **loads(body))

            elif action == 'CAPTURE':
                buffer = self.__process_capture(**loads(body))

            elif action == 'CANCEL':
                buffer = self.__process_cancel(**loads(body))

            elif action == 'QUERYBIN':
                buffer = self.__processo_query_bin(**loads(body))

            else:
                Exception('Ação não suportada: {}'.format(action))
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

        :return:
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('PaymentCieloExecutor em execução!')

        channel = create_new_connection('PAYMENT CIELO').channel()
        channel.basic_consume(self.callback, queue='queue_PAYMENT_CIELO', no_ack=False)
        channel.start_consuming()

        self.__event.wait()

        channel.stop_consuming()

    def stop(self):
        """
        Solicita a finalização da Thread de MicroContract
        """
        self.__event.set()
        self.join()
