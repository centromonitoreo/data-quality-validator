from typing import List
from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.generate_ids import GenerateId


class GenerateIdService(ABC):

    @abstractmethod
    def get_generate_id_by_thematic(self, thematic_name) -> List[GenerateId]:
        pass