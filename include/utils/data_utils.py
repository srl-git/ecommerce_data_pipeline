import pandas as pd
import utils.logger as logger

log = logger.get_logger(__name__)


def check_columns(df: pd.DataFrame, expected_cols: list[str]) -> pd.DataFrame:
    """
    Validate DataFrame columns against list of expected columns.

    Extra columns in the DataFrame will be dropped with a warning.
    If any expected columns are missing, a ValueError is raised.

    Args:
        df (pd.DataFrame): Dataframe to validate.
        expected_cols (list[str]): List of expected column names.

    Returns:
        pd.DataFrame: The validated DataFrame with only the expected columns.
    
    Raises:
        ValueError: If any expected columns are missing from the DataFrame.
    """
    cols = df.columns.to_list()
    if cols == expected_cols:
        return df
    missing_cols = list(set(expected_cols) - set(cols))
    extra_cols = list(set(cols) - set(expected_cols))
    if extra_cols:
        log.warning(f'Dropping unexpected extra column(s) in data source: \n{extra_cols}')
        df = df.drop(columns=extra_cols)
    if missing_cols:
        raise ValueError(f'Missing column(s) in data source: \n{missing_cols}')
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame keeping the first occurence.

    Args:
        df (pd.DataFrame): Dataframe from which to remove duplicates.

    Returns:
        pd.DataFrame: A DataFrame with no duplicate rows.
    """
    return df.drop_duplicates(keep='first')


def check_unique(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Validate that the specified columns of a DataFrame are unique.

    Args:
        df (pd.DataFrame): The Dataframe to validate.
        cols (list[str]): The column names to check for uniqueness.

    Returns:
        pd.DataFrame: The validated DataFrame.

    Raises:
        ValueError if the given DataFrame columns aren't unique.
    """
    is_unique = df[cols].nunique() == len(df)
    if not is_unique.all():
        raise ValueError('Report contains duplicate primary keys')
    return df


def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove leading and trailing whitespace from all string columns in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to clean.

    Returns:
        pd.DataFrame: The cleaned DataFrame with stripped string values.
    """
    for col in df.select_dtypes(include=['object']).columns:
            df.loc[:, col] = df.loc[:, col].str.strip()
    return df


def clean_date_formats(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    """
    Convert specified columns in the DataFrame to datetime format.

    Args:
        df (pd.DataFrame): The DataFrame containing the date columns to convert.
        date_cols (list[str]): List of column names to convert to datetime.

    Returns:
        pd.DataFrame: The DataFrame with the specified columns converted to datetime dtype.
    """
    df.loc[:, date_cols] = df.loc[:, date_cols].apply(pd.to_datetime, errors='coerce', format='mixed', dayfirst=True)
    df = df.astype({col: 'datetime64[ns]' for col in date_cols})

    # Raises SettingWithCopyWarning:
    # for col in date_cols:
    #     df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed', dayfirst=True)
    return df


def clean_missing_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Forward/Backward fill missing values in datetime columns of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing datetime columns with missing values.

    Returns:
        pd.DataFrame: The DataFrame with missing datetime values filled.
    """
    for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        df.loc[:, col] = df.loc[:, col].ffill().bfill()
    return df


def check_ranges(df: pd.DataFrame, column_ranges: dict[str, list], drop: bool = False) -> pd.DataFrame:
    """
    Check if values in specified columns fall within the given ranges. Optionally drop rows with out-of-range values.

    Args:
        df (pd.DataFrame): The DataFrame to check.
        column_ranges (dict[str, list]): Dictionary where keys are column names and values are lists containing [min_value, max_value].
        drop (bool): If True, rows with out-of-range values are dropped. Default is False.

    Returns:
        pd.DataFrame: The DataFrame with out-of-range values logged and optionally dropped.

    Logs:
        A warning containing the column(s) with out-of-range values, along with the indices of the affected rows.
    """ 
    out_of_range = {}
    for col, [min_val, max_val] in column_ranges.items():
        mask = (df[col] < min_val) | (df[col] > max_val)
        out_of_range_indices = df.index[mask].tolist()
        if out_of_range_indices:
            out_of_range[col] = out_of_range_indices
    if out_of_range:
        log_str = 'Column(s) containing out of range values:\n'
        for col, indeces in out_of_range.items():
            log_str += f'{col}: {indeces}\n'
        log.warning(log_str)
        if drop:
            drop_rows = [row for rows in out_of_range.values() for row in rows]
            return df.drop(index=drop_rows)
    return df


def rename_columns(df: pd.DataFrame, cols: dict[str,str]) -> pd.DataFrame:
    """
    Rename columns of a DataFrame according to the provided mapping.

    Args:
        df (pd.DataFrame): The DataFrame whose columns are to be renamed.
        cols (dict[str, str]): A dictionary where keys are current column names and values are the new column names.

    Returns:
        pd.DataFrame: A DataFrame with the columns renamed according to the provided mapping.
    """
    df = df.rename(columns=cols)
    return df