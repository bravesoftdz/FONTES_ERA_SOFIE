# coding: utf-8

"""

"""

from argparse import ArgumentParser
from collections import namedtuple

from pika import BlockingConnection, URLParameters, PlainCredentials
from pika.connection import ConnectionParameters

from library.common.exception import MySofieException

params = ArgumentParser(
    prog='CortexStorage',
    usage='Storage Cortex da plataforma Sofie',
    description='Provê ponto centralizado de acesso ao RabbitMQ do Sofie'
)
params.add_argument('-x', '--cortex', help='URI de acesso ao storage Cortex', type=str, required=True)
ARGS = params.parse_known_args()[0]

ExchangeDeclare = namedtuple('ExchangeDeclare', ['doc', 'name', 'type', 'durable'])

QueueDeclare = namedtuple('QueueDeclare', ['doc', 'name', 'durable', 'exclusive'])

BindDeclare = namedtuple('BindDeclare', ['doc', 'exchange', 'queue', 'routing_key'])

DECLARE_QUEUES = [
    ExchangeDeclare('Micro Contrato', 'exchange_MICRO_CONTRACT', 'topic', True),
    QueueDeclare('Micro Contrato', 'queue_PROCESS_MICRO_CONTRACT', True, False),
    BindDeclare('Micro Contrato', 'exchange_MICRO_CONTRACT', 'queue_PROCESS_MICRO_CONTRACT', 'SOFIE.MICRO_CONTRACT.#'),

    ExchangeDeclare('Meios de Pagamento', 'exchange_PAYMENT', 'topic', True),
    QueueDeclare('Meios de Pagamento', 'queue_PAYMENT_CIELO', True, False),
    BindDeclare('Meios de Pagamento', 'exchange_PAYMENT', 'queue_PAYMENT_CIELO', 'PAYMENT.CIELO.#'),

    ExchangeDeclare('Livro Razão', 'exchange_LEDGER', 'topic', True),
    QueueDeclare('Livro Razão', 'queue_PROCESS_LEDGER', True, False),
    BindDeclare('Livro Razão', 'exchange_LEDGER', 'queue_PROCESS_LEDGER', 'SOFIE.LEDGER.#'),

    ExchangeDeclare('Prevenção de Fraude', 'exchange_FRAUD', 'topic', True),
    QueueDeclare('Prevenção de Fraude', 'queue_PROCESS_FRAUD_CLEARSALE', True, False),
    BindDeclare('Prevenção de Fraude', 'exchange_FRAUD', 'queue_PROCESS_FRAUD_CLEARSALE', 'SOFIE.FRAUD.PREVENTION.CLEAR_SALE.#'),

    ExchangeDeclare('Assistente Sofie', 'exchange_EMAIL_SOFIE', 'topic', True),
    QueueDeclare('Assistente Sofie', 'queue_PROCESS_EMAIL_SOFIE', True, False),
    BindDeclare('Assistente Sofie', 'exchange_EMAIL_SOFIE', 'queue_PROCESS_EMAIL_SOFIE', 'SOFIE.ASSISTANT_SOFIE.EMAIL.#'),

    ExchangeDeclare('Eventos para Analytics', 'exchange_ANALYTICS', 'topic', True),
    QueueDeclare('Eventos para Analytics', 'queue_PROCESS_ANALYTICS', True, False),
    BindDeclare('Eventos para Analytics', 'exchange_ANALYTICS', 'queue_PROCESS_ANALYTICS', 'SOFIE.ANALYTICS.#'),
]

url_params = URLParameters(ARGS.cortex)


def heartbeat_callback(_connection, _broker_val):
    """

    :param _connection:
    :param _broker_val:
    :return:
    """
    return _broker_val


def create_new_connection(connection_name: str) -> BlockingConnection:
    """

    :param connection_name:
        Identificação do client para fins de monitoração
    :return:
    """
    rabbit_params = ConnectionParameters(
        host=url_params.host,  #: Endereço IP do servidor
        port=url_params.port,  #: Porta TCP
        credentials=PlainCredentials('guest', 'guest'),  #: Credenciais de usuário
        heartbeat=heartbeat_callback,
        # heartbeat_interval=600, - ESTA PARÂMETRO CONSTA COMO DEPRECIADO
        # blocked_connection_timeout=300,  #: Tempo em SEGUNDOS
        client_properties={'consumer_name': connection_name}
    )

    return BlockingConnection(rabbit_params)


channel = create_new_connection('INICIANDO').channel()

for each in DECLARE_QUEUES:
    if isinstance(each, ExchangeDeclare):
        channel.exchange_declare(
            exchange=each.name,
            exchange_type=each.type,
            durable=each.durable
        )
    elif isinstance(each, QueueDeclare):
        channel.queue_declare(
            queue=each.name,
            durable=each.durable,
            exclusive=each.exclusive,
            auto_delete=False
        )
    elif isinstance(each, BindDeclare):
        channel.queue_bind(
            queue=each.queue,
            exchange=each.exchange,
            routing_key=each.routing_key
        )
    else:
        raise MySofieException('Classe não suportada: [{}]'.format(each.__class__.__name__))

channel.connection.close()


