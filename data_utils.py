import pandas as pd


def check_columns(df: pd.DataFrame, expected_cols: list[str]) -> pd.DataFrame:

    cols = df.columns.to_list()
    if cols == expected_cols:
        return df
    missing_cols = list(set(expected_cols) - set(cols))
    extra_cols = list(set(cols) - set(expected_cols))
    if extra_cols:
        print(f'Unexpected extra column(s) in data source: \n{extra_cols}')
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
            df[col] = df[col].str.strip()
    return df


def clean_date_formats(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    
    date_cols = [date_cols] if isinstance(date_cols, str) else date_cols
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed', dayfirst=True)
    return df


def clean_missing_dates(df: pd.DataFrame) -> pd.DataFrame:

    for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        df[col] = df[col].ffill().bfill()
    return df


def check_positive(df: pd.DataFrame, ignore_cols: list[str]=[]) -> pd.DataFrame:

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.difference(ignore_cols)
    negative_cols = numeric_cols[(df[numeric_cols] <= 0).any(axis=0)]
    
    if not negative_cols.empty:
            raise ValueError(f'Non-positive values in columns: \n{list(negative_cols)}.')
    return df


def check_outliers(df: pd.DataFrame) -> pd.DataFrame:

    id_cols = [col for col in df.columns if '_id' in col]
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.difference(id_cols)

    if not numeric_cols.empty:
        lower_bound = df[numeric_cols].quantile(0.01)
        upper_bound = df[numeric_cols].quantile(0.99)
        outliers = df[((df[numeric_cols] < lower_bound) | (df[numeric_cols] > upper_bound)).any(axis=1)]

        if not outliers.empty:
            print(f'Outlier values found in columns: {list(numeric_cols)}')
            print(outliers)           
    return df


def rename_columns(df: pd.DataFrame, cols: dict[str,str]) -> pd.DataFrame:

    df = df.rename(columns=cols)
    return df