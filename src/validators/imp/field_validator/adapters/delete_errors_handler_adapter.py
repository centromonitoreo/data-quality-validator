from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteTableErrors,
    DeleteData,
)
from typing import List

from collections import defaultdict


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: List[FieldTypeVerificationError], table_name: str):
        self.errors: List[FieldTypeVerificationError] = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        errors_grouped = defaultdict(list)

        for fields_type_errors in self.errors:
            for error_data in fields_type_errors.error_data:
                errors_grouped[fields_type_errors.column].append(error_data.index)

        errors_delete = [
            DeleteData(column=col, index=indices)
            for col, indices in errors_grouped.items()
        ]

        return DeleteErrorsInput(
            errors=[DeleteTableErrors(table_name=self.table_name, errors=errors_delete)]
        )
