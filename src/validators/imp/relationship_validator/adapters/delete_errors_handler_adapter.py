from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
from validators.imp.relationship_validator.schemas.schemas import RelationShipOutput
from error_handlers.imp.delete_strategy.schemas.schemas import (
    DeleteRows,
    DeleteTableErrors
)

from collections import defaultdict


class DeleteErrorHandlerAdapter:
    def __init__(self, errors: RelationShipOutput, table_name: str):
        self.errors: RelationShipOutput = errors
        self.table_name = table_name

    def adpter_errors(self) -> DeleteErrorsInput:

        grouped_errors = defaultdict(set)

        for name_layer, error_list in self.errors.errors.items():
            for error in error_list:
                grouped_errors[name_layer].update(error.index_error)
                for name_layer_relation, index_relation in error.relation_index.items():
                    grouped_errors[name_layer_relation].update(index_relation)

        all_errors = []
        for table_name, index_set in grouped_errors.items():
            errors_delete = DeleteTableErrors(
                table_name=table_name,
                errors=DeleteRows(index=sorted(index_set)),
            )
            all_errors.append(errors_delete)

        # all_errors = []

        # for name_layer, error_list in self.errors.errors.items():
        #     for error in error_list:
        #         temp_errors = []
                
        #         errors_delete = DeleteTableErrors(
        #             table_name=name_layer,
        #             errors=DeleteRows(index=error.index_error),
        #         )
        #         temp_errors.append(errors_delete)

        #         for name_layer_relation, index_relation in error.relation_index.items():
        #             errors_delete_relation = DeleteTableErrors(
        #                 table_name=name_layer_relation,
        #                 errors=DeleteRows(index=index_relation),
        #             )
        #             temp_errors.append(errors_delete_relation)

        #         all_errors.extend(temp_errors)

        return DeleteErrorsInput(errors=all_errors)