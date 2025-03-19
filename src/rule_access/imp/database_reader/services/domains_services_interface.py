from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.domain import DomainTable
from typing import List

class DomainTableService(ABC):

    @abstractmethod
    def get_domains_by_domain_name(self, domain_name) -> List[DomainTable]:
        pass

    