from sqlalchemy.orm import Session
from rule_access.imp.database_reader.models.tables import Table
from rule_access.imp.database_reader.models.thematic import Thematic
from typing import List
from rule_access.imp.database_reader.services.tables_services_interface import (
    TableService,
)
from rule_access.imp.database_reader.config import SessionManager
import uuid


class TableServiceImpl(TableService):

    def get_tables_by_thematic(self, thematic: str) -> List[Table]:
        return (
            SessionManager()
            .get_session()
            .query(Table)
            .join(Thematic)
            .filter(Thematic.nombre_grupo == thematic)
            .all()
        )

    def get_table_by_id(self, table_id: uuid.uuid4) -> Table:
        return (
            SessionManager()
            .get_session()
            .query(Table)
            .filter(Table.id == table_id)
            .first()
        )
