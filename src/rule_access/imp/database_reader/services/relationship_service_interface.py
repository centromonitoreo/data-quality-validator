from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.relationships import Relationship
from typing import List

class RelationshipService(ABC):

    @abstractmethod
    def get_relationship_by_table(self, table_name) -> List[Relationship]:
        pass

    