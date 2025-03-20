from typing import List
from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.relationships import Relationship


class RelationshipService(ABC):

    @abstractmethod
    def get_relationship_by_thematic(self, thematic_name) -> List[Relationship]:
        pass
