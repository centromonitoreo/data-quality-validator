from rule_access.imp.database_reader.services.validations_thematic_interface import (
    ValidationThematicService,
)
from rule_access.imp.database_reader.models.validation_thematic import (
    ValidationThematic,
)
from rule_access.imp.database_reader.models.thematic import Thematic
from rule_access.imp.database_reader.config import SessionManager
from typing import List


class ValidationThematicServiceImp(ValidationThematicService):

    def get_validations_by_thematic(
        self, thematic_name: str
    ) -> List[ValidationThematic]:
        return (
            SessionManager()
            .get_session()
            .query(ValidationThematic)
            .join(Thematic)
            .filter(Thematic.nombre_grupo == thematic_name)
            .all()
        )
