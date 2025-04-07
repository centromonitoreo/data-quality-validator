
from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError, MandatoryErrorData
from error_handlers.imp.delete_strategy.schemas.schemas import DeleteRows, DeleteTableErrors, DeleteData
from typing import List

class DeleteErrorHandlerAdapter:
    def __init__(self, errors: List[FieldTypeVerificationError], table_name:str):
        self.errors: FieldTypeVerificationError = errors
        self.table_name = table_name
        

    def adpter_erros(self) -> DeleteErrorsInput:
            errors_schemas = []
            delete_index = []
            for error in self.errors.list_errors:
                if isinstance(error, MandatoryErrorData):
                    delete_index.extend(error.list_index)
                if delete_index:
                    DeleteTableErrors(table_name=self.table_name, erros=DeleteRows(index=delete_index))
                    errors_schemas.append(DeleteTableErrors)
            for error in self.errors.list_errors:
                if not isinstance(error, MandatoryErrorData):
                    errors_schemas.append(
                         DeleteData(
                            column = error.column,
                            index = [e.index for e in error.error_data if e.index not in delete_index]
                            )
                    )

            return errors_schemas