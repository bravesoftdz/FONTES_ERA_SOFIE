# coding: utf-8

"""
Aglutina as regras de negócio relacionado ao processo de Challenge
"""

from collections import defaultdict
from random import shuffle

from crud.card import CardCRUD
from crud.company import CompanyCRUD
from crud.know import CardKnowCRUD
from library.common.exception import MySofieException
from library.common.governance import DEVELOPER_SESSION, LEVEL_SOFIER, LEVEL_DEVELOPER
from library.common.miscellaneous import sanitize_text
from library.common.paging_info import PagingInfo
from library.crud.crud_base import CRUDBase, AllowedLevels
from library.storage.caching import apply_caching
from library.storage.relation import RelationStorage


class CardDontMatchWithSofier(MySofieException):
    """
    Indica que o Card solicitado pelo Sofier não é visível ao mesmo
    """

    def __init__(self, sofier: str, card: str):
        """
        Inicializa o objeto
        """
        self.__sofier = sofier
        self.__card = card
        super().__init__(f'O cartão [{self.__card}] não é visível ao sofier [{self.__sofier}]')

    def card(self):
        """
        Expõe o atributo que armazena o nome do Card

        :return:
            `str`
        """
        return self.__card

    def sofier(self):
        """
        Expõe o atributo que armazena o nome do Sofier

        :return:
            `str`
        """
        return self.__sofier


class ChallengeCRUD(CRUDBase):
    """

    """

    resource_class = 'challenge'

    scheme = None

    CYPHER_SUMMARY = """
    MATCH (company:COMPANY)-[:OFFER]->(card:CARD)
    RETURN company, card    
    """

    CYPHER_CARDS = """
    MATCH (card:CARD{expertise:{expertise}})<-[:OFFER]-(company:COMPANY)
    RETURN card 
    """

    CYPHER_CARD_MATCH_SOFIER = """
    MATCH (card:CARD{name:{card}})<-[:OFFER]-(company:COMPANY)
    RETURN card.name
    """

    levels_permissions = AllowedLevels(
        listing=[LEVEL_DEVELOPER, LEVEL_SOFIER],
        item=[LEVEL_DEVELOPER, LEVEL_SOFIER],
        create=[LEVEL_DEVELOPER, LEVEL_SOFIER],
        archive=[LEVEL_DEVELOPER, LEVEL_SOFIER],
        modify=[LEVEL_DEVELOPER, LEVEL_SOFIER]
    )

    def get_sample(self) -> dict:
        """
        Recupera uma **amostra** dos cards.

        A amostra é aleatória para passar ao Sofier uma sensação de diversidade

        :return:
        """

        @apply_caching('MYSOFIE:CACHE:CARDS:BYCATEGORY#')
        def get_cards_id_by_category() -> dict:
            """

            :return:
            """
            cursor = CardCRUD(PagingInfo(), DEVELOPER_SESSION).collection.aggregate([
                {'$match': {'__archived__': {'$exists': False}}},
                {'$unwind': '$categories'},
                {'$group': {'_id': '$categories', 'cards': {'$addToSet': '$name'}}}
            ])

            return {each['_id']: each['cards'] for each in cursor}

        pre_return = get_cards_id_by_category()
        for key, value in pre_return.items():
            shuffle(value)
            pre_return[key] = value[:5]

        return {'items': pre_return}

    @apply_caching('MYSOFIE:CACHE:SOFIER:{0.sofier}:CHALLENGE:SUMMARY#', ttl=60 * 60 * 24 * 7)
    def get_summary(self) -> dict:
        """
        Recupera o resumo de cards do _sofier_ para um primeiro posicionamento da área "Desafios"

        Classes de recursos envolvidas:
        ------------------------------

        - CARD
        - COMPANY
        - SOFIER

        :return:
            Dicionário que representa o resumo
        """

        def build_dict():
            return {'total': 0, 'news': 0}

        companies = CompanyCRUD(PagingInfo(fields=['name', 'card_bookmark_color']), DEVELOPER_SESSION).listing()['data']

        pipeline = list()
        if self.session.sofier_alpha:
            pipeline.append({'$match': {'in_homologation': False}})
        pipeline.append({'$group': {'_id': '$expertise', 'qtt': {'$sum': 1}}})

        cursor_expertises = CardCRUD(PagingInfo(), DEVELOPER_SESSION).collection.aggregate(pipeline)

        expertises = defaultdict(build_dict)
        for each in cursor_expertises:
            expertises[each['_id']]['total'] = each['qtt']

        return {
            'sofier': self.session.user,
            'companies': companies,
            'expertises': expertises
        }

    @apply_caching('MYSOFIE:CACHE:SOFIER:{0.sofier}:CHALLENGE:{1}:{2}#', ttl=60 * 60 * 24 * 7)
    def get_cards_by_expertise(self, expertise: str, filter_: [str, None]):
        """
        Recupera a lista de Cards por um determinado expertise

        [Consulte o cartão](https://trello.com/c/CW88k17A)

        :param expertise:
            Nome do expertise
        :param filter_:
            Filtro a ser aplicado
        :return:
            Dicionário representando a resposta
        """
        if filter_:
            normalized_filter = sanitize_text(filter_)
            normalized_filter = set(normalized_filter.split())

        def apply_filter(item: dict) -> bool:
            """

            :return:
            """
            set_target = set(sanitize_text(f'{item["title"]["title"]} {item["title"]["sub_title"]}').split())
            return normalized_filter.issubset(set_target)

        def get_companies() -> list:
            """

            :return:
            """
            buffer = list()

            list_companies = CompanyCRUD(PagingInfo(fields=['name', 'full_name', 'description']), DEVELOPER_SESSION).listing()['data']
            for company in list_companies:
                if normalized_filter.intersection(set(sanitize_text(company['full_name']).split())):
                    buffer.append(company)

            return buffer

        projection = {'name': 1, 'company': 1, 'title.title': 1, 'title.sub_title': 1, 'bookmarks.card': 1, 'payment_conditions.reward': 1, '_id': 0}
        criterias = {'expertise': expertise}
        if not self.session.sofier_alpha:
            criterias['in_homologation'] = False

        cards = [each for each in CardCRUD(PagingInfo(), DEVELOPER_SESSION).collection.find(filter=criterias, projection=projection)]

        for card in cards:
            conditions = card.pop('payment_conditions')
            card['max_reward'] = max([each['reward'] for each in conditions])

        if filter_:
            cards = [item for item in filter(apply_filter, cards)]

        return {'cards': {'expertise': expertise, 'list': cards}, 'companies': get_companies() if filter_ else list()}

    def get_card_cover(self, card: str) -> tuple:
        """

        :param card:
        :return:
        """
        return CardCRUD(PagingInfo(), DEVELOPER_SESSION).recover_image(card)

    def get_card_detail(self, card: str, level: str) -> dict:
        """

        :param card:
        :param level:
        :return:
        """
        cursor = RelationStorage().run(ChallengeCRUD.CYPHER_CARD_MATCH_SOFIER, card=card)

        is_valid = False
        for item in cursor:
            is_valid = item['card.name'] == card

        if not is_valid:
            raise CardDontMatchWithSofier(self.session.user, card)

        if level == 'less_detail':
            fields = [
                'name',
                'title.title',
                'title.sub_title',
                'payment_conditions.quotes.qtt',
                'payment_conditions.quotes.value',
                'payment_conditions.quotes.with_rate',
                'payment_conditions.method',
                'payment_conditions.title',
                'bookmarks.card.row_1',
                'bookmarks.card.row_2',
                'bookmarks.card.row_3',
            ]

        elif level == 'detail':
            fields = [
                'name',
                'company',
                'expertise',
                'description',
                'title.title',
                'title.sub_title',
                'title.row_1',
                'title.row_2',
                'payment_conditions.quotes.qtt',
                'payment_conditions.quotes.value',
                'payment_conditions.quotes.with_rate',
                'payment_conditions.method',
                'payment_conditions.title',
                'bookmarks.card.display',
                'bookmarks.card.row_1',
                'bookmarks.card.row_2',
                'bookmarks.card.row_3',
                'bookmarks.detail_1.display',
                'bookmarks.detail_1.row_1',
                'bookmarks.detail_1.row_2',
                'bookmarks.detail_1.row_3',
                'bookmarks.detail_2.display',
                'bookmarks.detail_2.row_1',
                'bookmarks.detail_2.row_2',
                'bookmarks.detail_2.row_3',
                'bookmarks.detail_3.display',
                'bookmarks.detail_3.row_1',
                'bookmarks.detail_3.row_2',
                'bookmarks.detail_3.row_3',
            ]

        else:
            fields = []

        return CardCRUD(PagingInfo(fields=fields), DEVELOPER_SESSION).item(card)

    def set_card_know(self, card: str):
        """
        Cria um registro, no Config e Relation, de que o usuário tem conhecimento do Card

        :param card:
            Nome do Card
        """
        CardKnowCRUD(PagingInfo(), DEVELOPER_SESSION).register_card_know(self.session.user, card)

    @property
    def sofier(self):
        """

        :return:
        """
        return self.session.user
