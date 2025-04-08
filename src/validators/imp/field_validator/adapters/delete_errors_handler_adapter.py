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
        errors_delete = []

        for fields_type_errors in self.errors:
            for fields_type_errors_index in fields_type_errors.error_data:
                errors_delete.append(
                    DeleteData(
                        column=fields_type_errors.column,
                        index=[fields_type_errors_index.index]
                    )
                )

        return DeleteErrorsInput(
            errors=[DeleteTableErrors(table_name=self.table_name, errors=errors_delete)]
        )
