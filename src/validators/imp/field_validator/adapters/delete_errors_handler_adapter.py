from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteTableErrors,
    DeleteData,
)
from typing import List


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: List[FieldTypeVerificationError], table_name: str):
        self.errors: List[FieldTypeVerificationError] = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        errors_schemas = []
        for error in self.errors.list_errors:
            errors_schemas.append(
                DeleteData(
                    column=error.column, index=[e.index for e in error.error_data]
                )
            )

        return DeleteErrorsInput(
            errors=DeleteTableErrors(table_name=self.table_name, errors=errors_schemas)
        )
