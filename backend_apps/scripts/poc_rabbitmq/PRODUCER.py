from time import sleep
from uuid import uuid1
from random import choice

from pika import BlockingConnection, URLParameters, BasicProperties

print('::INICIANDO::')

conn = BlockingConnection(URLParameters('amqp://127.0.0.1:5672'))
channel = conn.channel()
channel.confirm_delivery()

OPTIONS = [i for i in range(1, 5)]
idx = 1
while True:
    try:
        task_id = str(uuid1())
        chosen = choice(OPTIONS)
    
        success = channel.basic_publish(
            exchange='MYSOFIE.EXCHANGE.MICRO_CONTRACT', # Nome do exchange
            routing_key='MYSOFIE.EVENT.MICRO_CONTRACT.{}.{}'.format(chosen, task_id), # Nome evento
            body='Mensagem #{} - [{}]- {}'.format(idx, chosen, task_id), # Corpo da mensagem
            properties=BasicProperties(delivery_mode=2) # Salvar em disco
        )
        print('Mensagem #{} [{}] enviada com {} - {}'.format(idx, chosen, 'sucesso' if success else 'INSUCESSO', task_id))
        idx += 1
        
        # sleep(1)
    except KeyboardInterrupt:
        break
        
conn.close()

print('::FINALIZANDO::')
