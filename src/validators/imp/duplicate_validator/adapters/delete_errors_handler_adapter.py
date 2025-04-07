from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyErrors
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteRows,
    DeleteTableErrors,
)


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: DuplicatesIdentifyErrors, table_name: str):
        self.errors: DuplicatesIdentifyErrors = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:
        error_index = []
        for error in self.errors.list_errors:
            error_index.extend(error.duplicate_index)
        return DeleteErrorsInput(
            errors=[DeleteTableErrors(
                table_name=self.table_name, errors=DeleteRows(index=error_index)
            )]
        )
