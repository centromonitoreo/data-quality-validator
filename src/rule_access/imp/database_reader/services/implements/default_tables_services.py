from sqlalchemy.orm import Session
from database.models.tables import Table
from database.models.thematic import Thematic
from typing import List
from services.tables_services_interface import TableService
from database.config import SessionManager

class TableServiceImpl(TableService):

    def get_tables_by_thematic(self, thematic: str) -> List[Table]:
        return SessionManager().get_session().query(Table).join(Thematic).filter(Thematic.nombre_grupo == thematic).all()