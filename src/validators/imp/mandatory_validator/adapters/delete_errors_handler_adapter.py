from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteRows,
    DeleteTableErrors,
    DeleteData,
)
from typing import List


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: List[FieldTypeVerificationError], table_name: str):
        self.errors: List[FieldTypeVerificationError] = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        
        for mandatory_error in self.errors:
            
            index = [e.index for e in error.errors]
            if self.errors.distribution_param_type == DistributionParamType.horizontal:
                table_errors.append(DeleteData(column=error.column_param, index=index))
            else:
                index_delete.extend(index)

        return DeleteErrorsInput(
            errors = DeleteTableErrors(
                table_name=self.table_name,
                errors=(
                    table_errors
                    if self.errors.distribution_param_type
                    == DistributionParamType.horizontal
                    else DeleteRows(index=index_delete)
                ),
            )
        )
