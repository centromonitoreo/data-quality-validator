from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.validation_thematic import (
    ValidationThematic,
)
from typing import List


class ValidationThematicService(ABC):

    @abstractmethod
    def get_validations_by_thematic(
        self, thematic_name: str
    ) -> List[ValidationThematic]:
        pass
