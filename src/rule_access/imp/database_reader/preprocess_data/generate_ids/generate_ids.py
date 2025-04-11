from typing import List, Any, Dict, Union, Set, Optional, Tuple

from rule_access.imp.database_reader.preprocess_data.generate_ids.schemas.schemas import GenerateIdInput
from rule_access.imp.database_reader.preprocess_data.generate_ids.generate_point_id import generate_points_id
from rule_access.imp.database_reader.preprocess_data.generate_ids.generate_sample_id import generate_sample_id


class IdGenerator():

    def __init__(self, generate_id_data=None, **kwargs):
        super().__init__(**kwargs)
        self.generate_id_data = generate_id_data
        self.errors: Dict[str, List[Any]] = {}
        
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        
        def propagate_father_id_field(data: Dict[str, Any], id_instructions: GenerateIdInput) -> Dict[str, Any]:
            """
            Propagates a specified ID field from the father table to child tables within the data dictionary.

            For each child table, this function performs a left merge with the father table based on the keys 'RADI',
            a specified join field, and additional validation columns if provided. It migrates the father's ID field to the 
            child table and adds a new column 'REV_CMRN' that is set to "Erroneo" if the migrated ID field is missing 
            (i.e., NaN, None, or null).
            """
            father_table_name = id_instructions.father_table
            father_df = data.get(father_table_name)
            father_id_field = id_instructions.id_anla
            join_field = id_instructions.id_gdb
            cols_validate = id_instructions.cols_validate
            cols_validate = [
                col_validate for col_validate in cols_validate if len(col_validate)>0
            ]

            # Define merge keys based on mandatory keys and optional validation columns.
            merge_keys = ['RADI', join_field]
            if cols_validate:
                merge_keys.extend(cols_validate)

            # Build a list of father dataframe columns required for merging.
            father_columns = ['RADI', join_field] + (cols_validate if cols_validate else []) + [father_id_field]

            for child_table in id_instructions.child_tables:
                child_df = data[child_table]
                child_df.drop(columns=[father_id_field], inplace = True, errors='ignore')
                # Merge the father's ID field into the child table using the defined merge keys.
                child_df = child_df.merge(
                    father_df[father_columns],
                    how='left',
                    on=merge_keys
                )
                # Add a review column that flags rows where the father's ID field is missing.
                child_df['REV_CMRN'] = child_df[father_id_field].isnull().map({True: "Erroneo", False: ""})
                data[child_table] = child_df

            return data


        # Generate IDs
        for id_instructions in self.generate_id_data:
            
            if id_instructions.is_point is True:
                data = generate_points_id(data, id_instructions)
            else:
                data = generate_sample_id(data, id_instructions)
                
            # Associated IDS to children tables 
            data = propagate_father_id_field(data, id_instructions)
        
        return data

    def validate_inputs(self):

        if self.generate_id_data is None or not isinstance(
            self.generate_id_data, list
        ):
            raise ValueError(
                "generate_id_data no está definido o no es una lista valida."
            )
        for generate_instructions in self.generate_id_data:
            if not isinstance(generate_instructions, GenerateIdInput):
                raise TypeError(
                    "Todos los elementos de generate_id_data deben ser de tipo GenerateIdInput."
                )
