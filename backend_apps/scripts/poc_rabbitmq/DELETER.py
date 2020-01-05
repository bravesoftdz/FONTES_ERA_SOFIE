from pika import BlockingConnection, ConnectionParameters

print('::INICIANDO::')

conn = BlockingConnection(ConnectionParameters(host='127.0.0.1'))

channel = conn.channel()

channel.queue_delete(queue='MYSOFIE.QUEUE.MICRO_CONTRACT')
channel.exchange_delete(exchange='MYSOFIE.EXCHANGE.MICRO_CONTRACT')

exchange = channel.exchange_declare(
    exchange='MYSOFIE.EXCHANGE.MICRO_CONTRACT',
    exchange_type='topic',
    durable=True
)

queue = channel.queue_declare(
    queue='MYSOFIE.QUEUE.MICRO_CONTRACT',
    durable=True,
    exclusive=False
)

channel.queue_bind(
    queue= queue.method.queue,
    exchange='MYSOFIE.EXCHANGE.MICRO_CONTRACT',
    routing_key='#' # Assinatura onde '*' ignora um segmento e '#' ignora vários segmentos
)

print('::FINALIZANDO::')