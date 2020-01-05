# coding: utf-8

from json import loads
from datetime import datetime

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop

AsyncHTTPClient.configure('tornado.simple_httpclient.SimpleAsyncHTTPClient', max_clients=5)


def resposta(response):
    """

    """
    if response.code == 200:
        texto = loads(response.body.decode())['balance']['final_balance']
    else:
        texto = str(response.error)

    print('RESPONDEU - {} - {} - {} - {}'.format(response.code, datetime.fromtimestamp(response.request.start_time).strftime('%H:%M:%S'), response.request_time, texto))


URL, USER, PWD = 'https://172.30.1.20/api/v2/sofier/me/balance/', '32379386889', '12345678'
# URL, USER, PWD = 'https://localhost:64000/api/v2/sofier/me/balance/', '19678335832', '12345678'

for i in range(0, 500):
    client = AsyncHTTPClient()

    request = HTTPRequest(URL, auth_username=USER, auth_password=PWD, request_timeout=120.0, connect_timeout=120.0)

    client.fetch(request, resposta)

IOLoop.current().start()
