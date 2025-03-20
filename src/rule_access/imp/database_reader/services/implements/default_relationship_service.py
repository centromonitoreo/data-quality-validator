from typing import List
from sqlalchemy import cast, String

from rule_access.imp.database_reader.services.relationship_service_interface import (
    RelationshipService,
)
from rule_access.imp.database_reader.models.relationships import Relationship
from rule_access.imp.database_reader.models.thematic import Thematic
from rule_access.imp.database_reader.config import SessionManager


class RelationshipServiceImp(RelationshipService):

    def get_relationship_by_thematic(self, thematic_name) -> List[Relationship]:
        return (
            SessionManager()
            .get_session()
            .query(Relationship)
            .join(Thematic)
            .filter(Thematic.nombre_grupo == thematic_name)
            .all()
        )
