from typing import List, Any, Dict, Union, Set, Optional, Tuple
import pandas as pd
import geopandas as gpd

from validators.interface import IValidator
from validators.imp.relationship_validator.schemas.schemas import (
    RelationShipInput,
    RelationshipError,
    RelationShipOutput,
)


class RelationshipDataValidator(IValidator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "relationship_data"):
            self.relationship_data = None
        self.errors: Dict[str, List[Any]] = {}

    def validate(self, data: Dict[str, Any]) -> RelationShipOutput:
        self.validate_inputs()
        errors_dict: Dict[str, List[RelationshipError]] = {}

        def build_relationship_structure(relationships: List[RelationShipInput]):
            nodes = {}

            def get_node(table_name: str) -> dict:
                if table_name not in nodes:
                    nodes[table_name] = {
                        "relations": {},
                        "key_name": None,
                    }
                return nodes[table_name]

            for rel in relationships:

                left_node = get_node(rel.left_table)
                right_node = get_node(rel.right_table)

                if left_node["key_name"] is None:
                    left_node["key_name"] = rel.left_key
                if right_node["key_name"] is None:
                    right_node["key_name"] = rel.right_key

                left_node["relations"][rel.right_table] = right_node

            right_tables = {r.right_table for r in relationships}
            left_tables = {r.left_table for r in relationships}
            root_tables = list(left_tables - right_tables)

            if len(root_tables) == 1:
                root_table = root_tables[0]
                return {root_table: nodes[root_table]}
            else:
                return {rt: nodes[rt] for rt in root_tables}
        
        def generate_tuples(df: pd.DataFrame, key_columns: List[str]) -> Set[Tuple[str, ...]]:
            return set(
                tuple(str(value).strip() for value in row)
                for row in df[key_columns].values
            )
       
        def search_in_relations(search_key: str, node: dict) -> dict:
            
            # Attempt to directly get the value for search_key in node
            if search_key in node:
                return node[search_key]
                 
            # If search_key exists in relations, return its associated value.
            only_value = next(iter(node.values()))
            relations = only_value.get("relations", {})
            if search_key in relations:
                return relations[search_key]
            return relations

        def find_node_key_with_search_key(search_key: str, node: dict) -> Union[str, None]:
            for node_key, content in node.items():
                relations = content.get("relations", {})
                if search_key in relations:
                    return node_key
            return None
        
        def find_missing_key_indices(df: pd.DataFrame, 
                             key_columns: List[str], 
                             missing_keys: Union[List[Tuple], Set[Tuple]]
                            ) -> List[int]:
            keys_series = df[key_columns].apply(lambda row: tuple(row), axis=1)
            indices = keys_series[keys_series.isin(missing_keys)].index.tolist()
            return indices
        
        def deep_missing_key_indices_son(
            parent_df: pd.DataFrame,
            index_error: List[int],
            node: Dict[str, Any],
            data: Dict[str, pd.DataFrame]
        ) -> Dict[str, Any]:

            results: Dict[str, Any] = {}
            relations = node.get("relations")
            if relations:
                for child_layer, child_node in relations.items():
                    col_name: str = child_node.get('key_name')
                    child_series = parent_df.loc[index_error, col_name]
                    keys_series = child_series.apply(lambda row: tuple(row), axis=1)
                    results[child_layer] = find_missing_key_indices(data[child_layer], col_name, keys_series)
            return results
        
        def deep_missing_key_indices_father(
            parent_df: pd.DataFrame,
            index_error: List[int],
            node: Dict[str, Any],
            grandfather_layer: str,
            data: Dict[str, pd.DataFrame]
        ) -> Dict[str, Any]:
            results: Dict[str, Any] = {}
            if grandfather_layer is not None:
                key_columns = node.get(grandfather_layer, {}).get('key_name')
                filtered_df = parent_df.loc[index_error, key_columns]
                keys_series = filtered_df.apply(lambda row: tuple(row), axis=1)
                results[grandfather_layer] = find_missing_key_indices(data[grandfather_layer], key_columns, keys_series)
            return results
            

        def validate_relationships_recursive(
            father_layer: str, node: dict, data: dict
        ) -> RelationShipOutput:

            errors: Dict[str, List[RelationshipError]] = {}

            # get father information
            if father_layer not in list(data.keys()):
                raise KeyError("Father information not found")
            parent_df = data.get(father_layer)
            
            union_children_keys: Set[Tuple] = set()
            
            node_to_eval = search_in_relations(father_layer, node)
            for child_layer, child_node in node_to_eval.get("relations", {}).items():
                
                # get foreign keys
                key_columns: List[str] = child_node.get("key_name", [])
                if not key_columns:
                    raise ValueError("Keys not found")
                
                # get son information
                if child_layer not in list(data.keys()):
                    raise KeyError("Children information not found")
                child_df = data.get(child_layer)
                
                # get unique foreign keys
                parent_keys: Set[Tuple] = generate_tuples(parent_df, key_columns)
                child_keys: Set[Tuple] = generate_tuples(child_df, key_columns)
                union_children_keys = union_children_keys.union(child_keys)
                
                # eval missing keys 
                missing_keys = list(child_keys - parent_keys)
                if missing_keys:
                    index_error = find_missing_key_indices(child_df, key_columns, missing_keys)
                    relation_index = deep_missing_key_indices_son(child_df, index_error, child_node, data)
                    error = RelationshipError(
                        key_columns=tuple(key_columns),
                        missing_keys=missing_keys,
                        index_error=index_error,
                        relation_index=relation_index
                    )
                    errors.setdefault(child_layer, []).append(error)

                # eval next son
                if child_node.get("relations"):
                    child_output = validate_relationships_recursive(
                        child_layer, node, data
                    )
                    for table, err_list in child_output.errors.items():
                        errors.setdefault(table, []).extend(err_list)

            if node_to_eval.get("relations"):
                missing_keys = list(parent_keys - union_children_keys)
                if missing_keys:
                    
                    grandfather_layer = find_node_key_with_search_key(father_layer, node)
                    index_error = find_missing_key_indices(parent_df, key_columns, missing_keys)
                    relation_index = deep_missing_key_indices_father(
                        parent_df,
                        index_error,
                        node,
                        grandfather_layer,
                        data
                    )
                    
                    error = RelationshipError(
                        key_columns=tuple(key_columns),
                        missing_keys=missing_keys,
                        index_error=index_error,
                        relation_index=relation_index
                    )

                    errors.setdefault(child_layer, []).append(error)

            return RelationShipOutput(errors=errors)

        def validate_all_relationships(
            relationship_structure: dict, data: dict
        ) -> RelationShipOutput:

            all_errors: Dict[str, List[RelationshipError]] = {}

            for root_layer, _ in relationship_structure.items():
                output = validate_relationships_recursive(root_layer, relationship_structure, data)
                for table, errs in output.errors.items():
                    all_errors.setdefault(table, []).extend(errs)

            return RelationShipOutput(errors=all_errors)

        relationship_structure = build_relationship_structure(self.relationship_data)
        relation_errors = validate_all_relationships(relationship_structure, data)

        return relation_errors

    def validate_inputs(self):

        if self.relationship_data is None or not isinstance(
            self.relationship_data, list
        ):
            raise ValueError(
                "relationship_data no está definido o no es una lista valida."
            )
        for relation_data in self.relationship_data:
            if not isinstance(relation_data, RelationShipInput):
                raise TypeError(
                    "Todos los elementos de relationship_data deben ser de tipo RelationshipData."
                )
