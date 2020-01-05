# coding: utf-8

from requests import post

from micro_services.analytics.power_bi.get_token import PowerBIAuth


class PowerBIBase(object):
    URL_BASE = 'https://api.powerbi.com/v1.0/myorg/groups/'

    def __init__(self, workspace: str, dataset: str, table: str):
        self.__token = PowerBIAuth()
        self.__workspace = workspace
        self.__dataset = dataset
        self.__table = table

    def execute_post(self, content: dict):
        url = f'{PowerBIBase.URL_BASE}/{self.workspace}/datasets/{self.dataset}/tables/{self.table}/rows'

        headers = {
            'Authorization': 'Bearer {}'.format(self.__token.token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        post(url, json=content, headers=headers)

    @property
    def workspace(self):
        return self.__workspace

    @property
    def dataset(self):
        return self.__dataset

    @property
    def table(self):
        return self.__table
