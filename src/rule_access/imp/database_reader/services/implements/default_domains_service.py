from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.domain import DomainTable
from rule_access.imp.database_reader.services.domains_services_interface import DomainTableService
from rule_access.imp.database_reader.config import SessionManager
from typing import List

class DomainTableServiceImp(DomainTableService):

    def get_domains_by_domain_name(self, domain_name) -> List[DomainTable]:
        return SessionManager().get_session().query(DomainTable).filter(DomainTable.domain_name==domain_name).all()

    