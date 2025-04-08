from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteRows,
    DeleteTableErrors,
)
from typing import List


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: List[FieldTypeVerificationError], table_name: str):
        self.errors: List[FieldTypeVerificationError] = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        index_delete = []
        for mandatory_error in self.errors:
            index_delete.extend(mandatory_error.error_data.list_index)
        errors_delete = DeleteRows(index=list(set(index_delete)))    

        return DeleteErrorsInput(
            errors = [DeleteTableErrors(
                table_name=self.table_name,
                errors=errors_delete,
            )]
        )
