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
from collections import defaultdict


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: NaturalLimitsErros, table_name: str):
        self.errors: NaturalLimitsErros = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        
        if self.errors.distribution_param_type == DistributionParamType.vertical:
            index = []
            for natural_limits_vertical_errors in self.errors.errors:
                for natural_limits_vertical_errors_index in natural_limits_vertical_errors.errors:
                    index.append(natural_limits_vertical_errors_index.index)
            errors_delete = DeleteData(
                        column=natural_limits_vertical_errors.column_name,
                        index=index
                    )
        elif self.errors.distribution_param_type == DistributionParamType.horizontal:
            column_index_map = defaultdict(list)
            errors_delete = []
            for natural_limits_horizontal_errors in self.errors.errors:
                column = natural_limits_horizontal_errors.column_param
                for error in natural_limits_horizontal_errors.errors:
                    column_index_map[column].append(error.index)
            errors_delete = [
                DeleteData(column=col, index=indices)
                for col, indices in column_index_map.items()
            ]
            
        return DeleteErrorsInput(
            errors=[DeleteTableErrors(table_name=self.table_name, errors=errors_delete)]
        )
