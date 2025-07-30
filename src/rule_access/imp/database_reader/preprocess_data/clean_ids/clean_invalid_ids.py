import pandas as pd

def clean_rev_cmnr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the 'REV_CMRN' column by removing rows with the labels 'Erroneo' and 'Duplicado'.
    
    Args:
        df (pd.DataFrame): DataFrame to process.
        
    Returns:
        pd.DataFrame: Processed DataFrame with specified rows removed.
    """
    if 'rev_cmrn' in df.columns:
        df = df[~df['rev_cmrn'].isin(["Erroneo", "Duplicado"])]
    return df


def clean_empty_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes rows with NaN values in the 'id_anla' and 'id_mu_anla' columns. 
    If both columns exist, it first removes rows for 'id_anla' then for 'id_mu_anla'.
    
    Args:
        df (pd.DataFrame): DataFrame to process.
        
    Returns:
        pd.DataFrame: Processed DataFrame with rows containing NaN values in specified columns removed.
    """
    if 'id_anla' in df.columns:
        df = df.dropna(subset=['id_anla'])
    if 'id_mu_anla' in df.columns:
        df = df.dropna(subset=['id_mu_anla'])
    return df


def process_invalid_ids(validated_data: dict) -> dict:
    """
    Processes each DataFrame in the validated_data dictionary by applying the 'REV_CMRN' cleaning
    and removing rows with NaN in specified columns.
    
    Args:
        validated_data (dict): Dictionary with DataFrame values to process.
        
    Returns:
        dict: Dictionary with modified DataFrames.
    """
    processed_data = {}
    for key, df in validated_data.items():
        df = clean_rev_cmnr(df)
        df = clean_empty_ids(df)
        processed_data[key] = df
    return processed_data
