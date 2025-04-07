from typing import List

from rule_access.imp.database_reader.services.generate_ids_interface import (
    GenerateIdService,
)
from rule_access.imp.database_reader.models.generate_ids import GenerateId
from rule_access.imp.database_reader.models.thematic import Thematic
from rule_access.imp.database_reader.config import SessionManager


class GenerateIdServiceImp(GenerateIdService):

    def get_generate_id_by_thematic(self, thematic_name) -> List[GenerateId]:
        return (
            SessionManager()
            .get_session()
            .query(GenerateId)
            .join(Thematic)
            .filter(Thematic.group_name == thematic_name)
            .all()
        )
