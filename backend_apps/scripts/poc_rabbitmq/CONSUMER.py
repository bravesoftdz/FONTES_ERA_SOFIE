from time import sleep
from random import choice

from pika import BlockingConnection, URLParameters

print('::INICIANDO::')

conn = BlockingConnection(URLParameters('amqp://127.0.0.1:5672'))
channel = conn.channel()
channel.basic_qos(prefetch_count=1)


def callback(channel, method, properties, body):
    # print(str(channel))
    # print(str(method))
    # print(str(properties))
    print(str(body))
    
    success = choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) % 2 == 0
    
    if success:
        channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        channel.basic_nack(delivery_tag=method.delivery_tag)
        
    sleep(1)
        
    print('SUCESSO' if success else 'INSUCESSO')
    
channel.basic_consume(callback, queue='MYSOFIE.QUEUE.MICRO_CONTRACT', no_ack=False)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    conn.close()
    
print('::FINALIZANDO::')

