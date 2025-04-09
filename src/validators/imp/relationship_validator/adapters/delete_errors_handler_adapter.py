from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.relationship_validator.schemas.schemas import RelationShipOutput
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteRows,
)


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: RelationShipOutput, table_name: str):
        self.errors: RelationShipOutput = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        index_delete = []