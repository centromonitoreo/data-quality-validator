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

        def record_missing_keys(
            errors: Dict[str, List[RelationshipError]],
            table: str,
            key_columns: List[str],
            source_keys: Set[Tuple],
            target_keys: Set[Tuple],
        ) -> None:
            missing_keys = list(source_keys - target_keys)
            if missing_keys:
                error = RelationshipError(
                    key_columns=tuple(key_columns), missing_keys=missing_keys
                )
                errors.setdefault(table, []).append(error)

        def validate_relationships_recursive(
            father_layer: str, node: dict, data: dict
        ) -> RelationShipOutput:

            errors: Dict[str, List[RelationshipError]] = {}

            if father_layer not in list(data.keys()):
                raise KeyError("Father information not found")

            parent_key_columns: List[str] = node.get("key_name", [])
            if not parent_key_columns:
                raise ValueError("Father keys not found")

            parent_df = data.get(father_layer)
            parent_keys: Set[Tuple] = set(
                tuple(row) for row in parent_df[parent_key_columns].values
            )

            union_children_keys: Set[Tuple] = set()

            for child_layer, child_node in node.get("relations", {}).items():
                if child_layer not in list(data.keys()):
                    raise KeyError("Children information not found")

                child_df = data.get(child_layer)
                child_key_columns: List[str] = child_node.get("key_name", [])
                if not child_key_columns:
                    raise ValueError("Children keys not found")

                child_keys: Set[Tuple] = set(
                    tuple(row) for row in child_df[child_key_columns].values
                )
                union_children_keys = union_children_keys.union(child_keys)

                record_missing_keys(
                    errors, child_layer, child_key_columns, child_keys, parent_keys
                )

                if child_node.get("relations"):
                    child_output = validate_relationships_recursive(
                        child_layer, child_node, data
                    )
                    for table, err_list in child_output.errors.items():
                        errors.setdefault(table, []).extend(err_list)

            if node.get("relations"):
                record_missing_keys(
                    errors,
                    father_layer,
                    parent_key_columns,
                    parent_keys,
                    union_children_keys,
                )

            return RelationShipOutput(errors=errors)

        def validate_all_relationships(
            relationship_structure: dict, data: dict
        ) -> RelationShipOutput:

            all_errors: Dict[str, List[RelationshipError]] = {}

            for root_layer, root_node in relationship_structure.items():
                output = validate_relationships_recursive(root_layer, root_node, data)
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
