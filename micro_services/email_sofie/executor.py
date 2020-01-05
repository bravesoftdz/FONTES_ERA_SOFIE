# coding: utf-8


from pickle import loads
from threading import Thread, Event

from library.storage.cortex import create_new_connection


class EmailExecutor(Thread):
    """
    Responsável por dar vazão aos emails do Assistente Sofie
    """

    def __init__(self):
        """
        Inicializa o objeto
        """
        self.__event = Event()
        super().__init__()

    def send_email(self, bytes_template: bytes):
        """
        Executa o envio de email

        :param bytes_template:
            Objeto de template de email recebido via Cortex
        """
        template = loads(bytes_template)
        template()

    def callback(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info(f'ENTROU -> {method.routing_key}')

        try:
            action = method.routing_key.split('.')[-1]

            if action == 'SEND':
                self.send_email(body)
            else:
                SERVICE_LOGGER.info(f'AÇÃO NÃO PREVISTA -> {action}')
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

        SERVICE_LOGGER.info(f'SAIU -> {method.routing_key}')

    def run(self):
        """

        :return:
        """
        from library.common.service_main import SERVICE_LOGGER
        SERVICE_LOGGER.info('EmailExecutor em execução!')

        channel = create_new_connection('EMAIL SOFIE').channel()
        channel.basic_consume(self.callback, queue='queue_PROCESS_EMAIL_SOFIE', no_ack=False)
        channel.start_consuming()

        self.__event.wait()

        channel.stop_consuming()

    def stop(self):
        """
        Solicita a finalização da Thread EmailExecutor
        """
        self.__event.set()
        self.join()
