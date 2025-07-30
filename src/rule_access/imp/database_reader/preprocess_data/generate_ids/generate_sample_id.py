import numpy as np
import pandas as pd
import geopandas as gpd

from rule_access.imp.database_reader.preprocess_data.generate_ids.schemas.schemas import GenerateIdInput

def filter_index(
    geopandas_database: gpd.GeoDataFrame, cols_merge: list, names: str
) -> pd.Series:
    """
    Filters the index of a GeoDataFrame based on specified column values.

    Parameters:
    - geopandas_database (gpd.GeoDataFrame): The GeoDataFrame to filter.
    - cols_merge (list): A list containing the names of the columns to filter.
    - names (str or list): The value(s) to filter for each column.

    Returns:
    - pd.Series: A boolean Series indicating the filtered index.

    Example:
        If `geopandas_database` is a GeoDataFrame, `cols_merge` is ['col1', 'col2'], and `names` is 'value',
        this function will filter the index of the GeoDataFrame based on the condition where 'col1' equals 'value'
        and 'col2' equals 'value' and return a boolean Series indicating the filtered index.

        filter_index(geopandas_database, ['col1', 'col2'], 'value')
    """

    if isinstance(names, str):
        names = [names]

    index_bool = pd.Series(True, index=geopandas_database.index)
    for col, name in zip(cols_merge, names):
        index_bool &= geopandas_database[col] == name
    return index_bool

def generate_sample_id(
    data: pd.DataFrame,
    id_instructions: GenerateIdInput,
) -> pd.DataFrame:
    """
    Generates sample IDs for records in a DataFrame based on specified criteria,
    iterating over each expedient group in the database.

    Parameters:
    - data (pd.DataFrame): The DataFrame containing the records.
    - id_instructions (GenerateIdInput): An object/dictionary specifying the father_table,
      id_anla, acronym, and id_gdb among other parameters.

    Returns:
    - pd.DataFrame: A DataFrame containing sample IDs and revision status for records.
    """
    
    database = data.get(id_instructions.father_table)
    database[id_instructions.id_anla] = np.nan
    database["rev_cmrn"] = np.nan
    acronym = id_instructions.acronym
    columns_generate_mu = ["radicado", id_instructions.id_gdb]

    # Iterate over each unique expedient in the database
    for expedient in set(database["expediente"]):
        # Create a mask to select only the rows for the current expedient
        mask_expedient = database["expediente"] == expedient
        # Filter the subset corresponding to the current expedient and drop rows without the necessary information
        subset = database[mask_expedient]
        df_group = subset.dropna(subset=columns_generate_mu)
        # Group the subset by the specified columns
        sample_group = df_group.groupby(columns_generate_mu)
        cont = 1  # Reset the counter for each expedient

        for names, values in sample_group:
            # Get the indices of rows that meet the group conditions for the current expedient and have no revision status yet
            indices = filter_index(database, columns_generate_mu, names) & mask_expedient & pd.isna(
                database["rev_cmrn"]
            )
            indices = database[indices].index.tolist()
            if len(indices) > 0:
                # Generate the sample ID using the acronym, current expedient, and the counter formatted to 4 digits
                id_anla_muestra = f"{acronym}-{expedient}-{str(cont).zfill(4)}"
                database.loc[indices, id_instructions.id_anla] = id_anla_muestra

                # Assign the revision status based on the number of records and the analysis dates
                if (len(values) > 1) and (len(values["fec_analis"].unique()) == 1):
                    database.loc[indices[0], "rev_cmrn"] = "Definitivo"
                    database.loc[indices[1:], "rev_cmrn"] = "Duplicado"
                elif (len(values) > 1) and (len(values["fec_analis"].unique()) > 1):
                    database.loc[indices, "rev_cmrn"] = "Erroneo"
                else:
                    database.loc[indices, "rev_cmrn"] = "Definitivo"
                cont += 1

    # Update data with the IDs generated 
    data[id_instructions.father_table] = database

    return data

