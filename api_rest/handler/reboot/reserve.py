# coding: utf-8

from http import HTTPStatus

from library.http.http_base import SofieHTTPHandler
from library.common.governance import LEVEL_APP_MYSOFIE
from handler.reboot.micro_task_reserve import MicroTaskReserve, dashboard, radar, create_micro_task


class MicroTaskHandler(SofieHTTPHandler):
    """
    Manipulador HTTP que insere uma micro tarefa na arena
    """

    def post(self):
        """
        Insere uma micro tarefa na arena
        """
        data = self.content_as_json

        b_ret = create_micro_task(data)
        self.write_json({'SUCCESS': b_ret})


class MicroTaskReserveHandler(SofieHTTPHandler):
    """
    Manipulador HTTP que efetiva, ou rejeita, a RESERVA de uma micro tarefa presencial
    """

    def post(self):
        """
        A fim de tornar a experiência mais fluída para a borda esta chamada cumpre dois papéis:

        1 - ACEITA ou REJEITA uma determinda micro tarefa presencial pelo seu código
        2 - Solicita uma micro tarefa presencial próxima à alguma coordenada geográfica.
        """
        p_sofier = self.get_argument('sofier', None)
        p_task_id = self.get_argument('task_id', None)
        p_action = self.get_argument('action', None)
        p_lat = self.get_argument('lat', None)
        p_lng = self.get_argument('lng', None)
        p_radius = self.get_argument('radius', None)

        mtr = MicroTaskReserve(p_sofier)
        if p_task_id:
            if p_action == 'accept':
                mtr.accept(p_task_id)
            elif p_action == 'reject':
                mtr.reject(p_task_id)
            else:
                raise Exception(f'Ação não reconhecida: [{p_action}]')

        if p_lat and p_lng:
            data = mtr.next_nearest(float(p_lat), float(p_lng), float(p_radius))

            if data:
                self.write_json(data, HTTPStatus.OK.value)
            else:
                self.write_json(force_status_code=HTTPStatus.NO_CONTENT.value)

        else:
            self.write_json(force_status_code=HTTPStatus.NO_CONTENT.value)

    def get(self):
        """
        Recupera todas as micro tarefas reservadas ao _sofier_
        """
        p_sofier = self.get_argument('sofier', None)

        mtr = MicroTaskReserve(p_sofier)
        data = mtr.get_reserveds()

        self.write_json(data, HTTPStatus.OK.value)


class MicroTaskExecutingHandler(SofieHTTPHandler):
    """
    Controla a execução de uma micro tarefa
    """

    def post(self, task_id: str, action: str):
        """
        Indica ao sistema se uma micro tarefa foi inicializada ou finalizada

        :param task_id:
            ID da micro tarefa
        :param action:
            Ação a ser executada
        """
        p_sofier = self.get_argument('sofier', None)

        mtr = MicroTaskReserve(p_sofier)

        if action == 'start':
            data = mtr.execution_start(task_id)
        elif action == 'finish':
            postpone_or_cancel = self.get_argument('postpone_or_cancel', 'FINISH')
            data = mtr.execution_finish(task_id, postpone_or_cancel)
        else:
            raise Exception(f'Ação não suportada: [{action}]')

        self.write_json(data, HTTPStatus.OK.value)


class MicroTaskDashboardHandler(SofieHTTPHandler):
    """
    Quantifica as localidades "RESERVADAS" e "EM EXECUÇÃO"
    """

    def get(self):
        """
        Quantifica as localidades "RESERVADAS" e "EM EXECUÇÃO"
        """
        self.write_json(dashboard())


class MicroTaskRadarHandler(SofieHTTPHandler):
    """
    Retorna todas as micro tarefas presenciais de acordo com as coordenadas geográficas passadas e raio
    """

    def get(self):
        """
        Retorna todas as micro tarefas presenciais de acordo com as coordenadas geográficas passadas e raio
        """
        p_lat = self.get_argument('lat', None)
        p_lng = self.get_argument('lng', None)
        p_radius = self.get_argument('radius', None)
        p_sofier = self.get_argument('sofier', None)

        self.write_json(radar(float(p_lat), float(p_lng), float(p_radius), p_sofier))


HANDLERS = [
    ['micro_task/?', MicroTaskHandler, {'POST': [LEVEL_APP_MYSOFIE]}, 'micro_task'],
    ['micro_task/dashboard/?', MicroTaskDashboardHandler, {'GET': [LEVEL_APP_MYSOFIE]}, 'micro_task_dashboard'],
    ['micro_task/radar/?', MicroTaskRadarHandler, {'GET': [LEVEL_APP_MYSOFIE]}, 'micro_task_radar'],
    ['micro_task/reserve/?', MicroTaskReserveHandler, {'POST': [LEVEL_APP_MYSOFIE], 'GET': [LEVEL_APP_MYSOFIE]}, 'micro_task_reserve'],
    ['micro_task/execution/(?P<task_id>[^/]+)/(?P<action>(?:start|finish))/?', MicroTaskExecutingHandler, {'POST': [LEVEL_APP_MYSOFIE]}, 'micro_task_start'],
]
