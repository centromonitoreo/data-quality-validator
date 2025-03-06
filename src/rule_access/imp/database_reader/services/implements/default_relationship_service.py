from rule_access.imp.database_reader.services.relationship_service_interface import RelationshipService
from rule_access.imp.database_reader.models.relationships import Relationship
from rule_access.imp.database_reader.models.tables import Table
from rule_access.imp.database_reader.config import SessionManager
from typing import List

class RelationshipServiceImp(RelationshipService):

    def get_relationship_by_table(self, table_name)  -> List[Relationship]:
        table = SessionManager().get_session().query(Table).filter(Table.name==table_name).first()
        return SessionManager().get_session().query(Relationship).filter(Relationship.left_table_id == str(table.id)).all()

