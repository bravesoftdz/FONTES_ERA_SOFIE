# coding: utf-8

from library.crud.crud_base import CRUDBase
from scheme.lead import SCHEME_LEAD


class LeadCRUD(CRUDBase):
    """

    """
    resource_class = 'lead'

    scheme = SCHEME_LEAD
