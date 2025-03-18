import pandas as pd
import logger

log = logger.get_logger(__name__)


def check_columns(df: pd.DataFrame, expected_cols: list[str]) -> pd.DataFrame:

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

    return df.drop_duplicates(keep='first')


def check_unique(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:

    is_unique = df[cols].nunique() == len(df)
    if not is_unique.all():
        raise ValueError('Report contains duplicate primary keys')
    return df


def clean_strings(df: pd.DataFrame) -> pd.DataFrame:

    for col in df.select_dtypes(include=['object']).columns:
            df.loc[:, col] = df.loc[:, col].str.strip()
    return df


def clean_date_formats(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    
    df.loc[:, date_cols] = df.loc[:, date_cols].apply(pd.to_datetime, errors='coerce', format='mixed', dayfirst=True)
    df = df.astype({col: 'datetime64[ns]' for col in date_cols})

    # Raises SettingWithCopyWarning:
    # for col in date_cols:
    #     df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed', dayfirst=True)
    return df


def clean_missing_dates(df: pd.DataFrame) -> pd.DataFrame:

    for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        df.loc[:, col] = df.loc[:, col].ffill().bfill()
    return df


def check_ranges(df: pd.DataFrame, column_ranges: dict[str, list], drop: bool = False) -> pd.DataFrame:
        
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

    df = df.rename(columns=cols)
    return df