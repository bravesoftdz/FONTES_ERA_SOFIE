from time import sleep
from random import choice

from pika import BlockingConnection, URLParameters

print('::INICIANDO::')

conn = BlockingConnection(URLParameters('amqp://127.0.0.1:5672'))
channel = conn.channel()

queue = channel.queue_declare(
    queue='',
    durable=True,
    exclusive=True
)
print(queue.method.queue)

channel.queue_bind(
    queue.method.queue,
    exchange='MYSOFIE.EXCHANGE.MICRO_CONTRACT',
    routing_key='MYSOFIE.EVENT.MICRO_CONTRACT.2.*' # Assinatura onde '*' ignora um segmento e '#' ignora vários segmentos
)

def callback(channel, method, properties, body):
    # print(str(channel))
    # print(str(method))
    # print(str(properties))
    print(str(body))
    
channel.basic_consume(callback, queue=queue.method.queue, no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    conn.close()
    
print('::FINALIZANDO::')

