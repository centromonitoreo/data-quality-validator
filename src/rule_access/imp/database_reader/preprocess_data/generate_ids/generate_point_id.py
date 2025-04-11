from typing import Union, Dict
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from rule_access.imp.database_reader.preprocess_data.generate_ids.schemas.schemas import (
    GenerateIdInput,
)


def fill_empty_geometries(
    gdf: gpd.GeoDataFrame, default_point: tuple = (0, 0), revision_col: str = "REV_CMRN"
) -> gpd.GeoDataFrame:
    """
    Fills empty or missing geometries in a GeoDataFrame with a default point (0,0)
    and marks these records as 'Erroneo' in the specified revision column.

    Parameters:
        gdf (geopandas.GeoDataFrame): Input GeoDataFrame.
        default_point (tuple, optional): Coordinates to use for filling empty geometries. Defaults to (0, 0).
        revision_col (str, optional): Column name where records with empty geometries will be marked as 'Erroneo'.
                                      Defaults to "REV_CMRN".

    Returns:
        geopandas.GeoDataFrame: Updated GeoDataFrame with empty geometries filled and marked.
    """
    # Create a mask for rows where the geometry is either missing or empty
    mask = gdf["geometry"].isnull() | gdf["geometry"].apply(
        lambda geom: geom.is_empty if geom is not None else True
    )

    # Fill empty geometries with the default point
    gdf.loc[mask, "geometry"] = Point(default_point)

    # Mark these records as 'Erroneo' in the revision column
    gdf.loc[mask, revision_col] = "Erroneo"

    return gdf


def inspect_id_consistency(df: pd.DataFrame, id_gdb: str) -> pd.DataFrame:
    """
    Checks the consistency of IDs by comparing rounded geometries.
    If a group defined by id_gdb and RADI contains more than one unique geometry,
    the records are marked as 'Erroneo'.
    """
    # Round the geometry for comparison
    df["geometry"] = df.geometry.apply(lambda pt: Point(round(pt.x, 0), round(pt.y, 0)))
    id_columns = [id_gdb, "RADI"]
    subset = df.dropna(subset=id_columns)

    for group_vals, group_df in subset.groupby(id_columns):
        if group_df.geometry.nunique() > 1:
            df.loc[
                (df[id_gdb] == group_vals[0]) & (df["RADI"] == group_vals[1]),
                "REV_CMRN",
            ] = "Erroneo"
    return df


def calculate_bool_index(
    gdf: gpd.GeoDataFrame,
    point_relation_column: str,
    distance: Union[int, float],
    reference_index: int,
) -> pd.Series:
    """
    Calculates a boolean index based on the following conditions:
      - The point relation column is null.
      - REV_CMRN is null or marked as 'Erroneo'.
      - The distance to the reference point is less than or equal to the threshold.
      - The record's index is greater than the reference index.
    """
    mask_nan = pd.isna(gdf[point_relation_column])
    mask_rev = pd.isna(gdf.REV_CMRN) | (gdf.REV_CMRN == "Erroneo")
    mask_distance = gdf.distance(gdf.geometry[reference_index]) <= distance
    mask_index = gdf.index > reference_index
    return mask_nan & mask_rev & mask_distance & mask_index


def assign_anla_ids(
    gdf: gpd.GeoDataFrame, id_instructions: GenerateIdInput
) -> gpd.GeoDataFrame:
    """
    Assigns ANLA IDs to records in the GeoDataFrame grouped by expedient.
    For each expedient group, existing IDs are propagated to nearby records within a specified distance.
    For records without an ID, a new one is generated using the format (acronym-expedient-counter) and propagated
    to neighboring records within the same group. The coordinate fields (COOR_ESTE and COOR_NORTE) are overwritten
    with the originating record's values.
    """

    # Extract ID field, acronym, and distance threshold from the instructions.
    id_field = id_instructions.id_anla
    acronym = id_instructions.acronym
    distance = id_instructions.buffer_distance

    # Process records grouped by 'EXPEDIENTE'
    for expedient in gdf["EXPEDIENTE"].unique():

        # Define a mask for the current expedient group
        group_mask = gdf["EXPEDIENTE"] == expedient

        # # Propagate existing IDs within the current group
        # group_assigned_indices = gdf.loc[group_mask][gdf.loc[group_mask, id_field].notna()].index
        # for idx in group_assigned_indices:
        #     # Create mask for records in the group within the specified distance from the current record
        #     mask = group_mask & (gdf.distance(gdf.geometry[idx]) <= distance)
        #     gdf.loc[mask, id_field] = gdf.loc[idx, id_field]

        # Initialize a counter for new IDs within this group.
        counter = 1

        # Iterate over records in the current group to assign new IDs where missing.
        for i in gdf.loc[group_mask].index:
            if pd.isna(gdf.at[i, id_field]):
                # Generate a new ID using the specified format.
                new_id = f"{acronym}-{expedient}-{str(counter).zfill(4)}"
                gdf.at[i, id_field] = new_id
                # Determine nearby records in the same group that should inherit the new ID.
                mask = group_mask & calculate_bool_index(gdf, id_field, distance, i)
                # Propagate the new ID and update coordinate fields.
                gdf.loc[mask, id_field] = new_id
                gdf.loc[mask, "COOR_ESTE"] = gdf.at[i, "COOR_ESTE"]
                gdf.loc[mask, "COOR_NORTE"] = gdf.at[i, "COOR_NORTE"]
                counter += 1

    return gdf


def filter_index(gdf: gpd.GeoDataFrame, cols: list, values: str) -> pd.Series:
    """
    Returns a boolean index that filters the GeoDataFrame for rows where the specified columns equal the given values.
    """
    if isinstance(values, str):
        values = [values]
    mask = pd.Series(True, index=gdf.index)
    for col, val in zip(cols, values):
        mask &= gdf[col] == val
    return mask


def classify_grouped_records(
    gdf: gpd.GeoDataFrame, id_instructions: GenerateIdInput
) -> gpd.GeoDataFrame:
    """
    Classifies grouped records by arbitrarily selecting the first record in each group as definitive.
    All other records in the group are marked as duplicates.
    """
    id_field = id_instructions.id_anla
    cols_validate = id_instructions.cols_validate
    cols_validate = [
        col_validate for col_validate in cols_validate if len(col_validate)>0
    ]
    # Build the list of columns to group by
    group_cols = [id_field] + (
        cols_validate
        if isinstance(cols_validate, list)
        else [cols_validate] if cols_validate else []
    )

    # Filter records that have the necessary grouping values
    valid_df = gdf.dropna(subset=group_cols)
    grouped = valid_df.groupby(group_cols)

    # Process each group of records
    for _, group_df in grouped:
        indices = group_df.index.tolist()
        # If the group has a single record, mark it as definitive
        if len(indices) == 1:
            gdf.at[indices[0], "REV_CMRN"] = "Definitivo"
        else:
            # Arbitrarily choose the first record as definitive and mark the rest as duplicates
            definitive_idx = indices[0]
            gdf.at[definitive_idx, "REV_CMRN"] = "Definitivo"
            for idx in indices[1:]:
                gdf.at[idx, "REV_CMRN"] = "Duplicado"

    return gdf


def generate_points_id(
    data: Dict[str, Union[gpd.GeoDataFrame, pd.DataFrame]],
    id_instructions: GenerateIdInput,
) -> Dict[str, Union[gpd.GeoDataFrame, pd.DataFrame]]:
    """
    Orchestrates the generation of ANLA IDs for points.
    Cleans temporary ID values, prepares fields, creates a GeoDataFrame (if possible),
    checks ID consistency, assigns new IDs, and classifies records as 'Definitivo' or 'Duplicado'.
    Returns data updated.
    """
    # Retrieve ID fields from the configuration dictionary
    id_field = id_instructions.id_anla
    id_gdb = id_instructions.id_gdb

    # Remove temporary values containing "TEM" by setting them to NaN
    database = data.get(id_instructions.father_table)
    # database[id_field] = database[id_field].apply(
    #     lambda x: np.nan if isinstance(x, str) and "TEM" in x else x
    # )
    database[id_field] = np.nan

    # Initialize the revision flag column to NaN
    database["REV_CMRN"] = np.nan

    # Clean up the id_gdb and RADI columns by stripping extra whitespace
    database[id_gdb] = database[id_gdb].astype(str).str.strip()
    database["RADI"] = database["RADI"].astype(str).str.strip()

    # Eval concistency of the information
    database = fill_empty_geometries(database)
    database = inspect_id_consistency(database, id_gdb)

    # Assign new ANLA IDs and propagate them to nearby records
    database = assign_anla_ids(database, id_instructions)

    # Stablish status by IDs
    database = classify_grouped_records(database, id_instructions)

    # Delete duplicates and erroneous register

    # Update data with the IDs generated
    data[id_instructions.father_table] = database

    return data
