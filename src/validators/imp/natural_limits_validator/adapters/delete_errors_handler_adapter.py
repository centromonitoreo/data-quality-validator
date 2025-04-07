from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.natural_limits_validator.schemas.schemas import (
    NaturalLimitsErros,
    DistributionParamType,
)
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteRows,
    DeleteTableErrors,
    DeleteData,
)
from typing import List


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: NaturalLimitsErros, table_name: str):
        self.errors: NaturalLimitsErros = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        table_errors = []
        index_delete = []
        for error in self.errors:
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
