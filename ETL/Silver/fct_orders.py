import os
from dotenv import load_dotenv
import pandas as pd
import google_cloud_storage_utils as gcs


def load_report(report_date: str) -> pd.DataFrame:

    bucket_name = os.getenv('bucket_name')
    report_name = f'order_reports/Order_report_{report_date}.csv'
    return pd.read_csv(f'gcs://{bucket_name}/{report_name}')


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


def check_unique_ids(df: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:

    id_cols = [id_cols] if isinstance(id_cols, str) else id_cols
    for col in id_cols:
        if not df[col].is_unique:
            raise ValueError('Report contains duplicate primary keys')
    return df


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame: 

    for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
    return df


def clean_date_formats(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:

    date_cols = [date_cols] if isinstance(date_cols, str) else date_cols
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed', dayfirst=True,)
    return df


def clean_missing_dates(df: pd.DataFrame) -> pd.DataFrame:

    for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        df[col] = df[col].ffill().bfill()
    return df


def clean_missing_prices(df: pd.DataFrame) -> pd.DataFrame:

    df['item_price'] = df.groupby('item_sku')['item_price'].transform(lambda x: x.ffill().bfill()) # fill price from other rows
    # df['item_price'] = df['item_price'].fillna(df['item_sku'].map(prices)) # fill price from database as dict
    return df

def add_line_total_col(df: pd.DataFrame) -> pd.DataFrame:

    df['line_total'] = df['qty'] * df['item_price']
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 7, 6]]
    return df

def load_to_bq(df: pd.DataFrame) -> None:

    gc_project_id = os.getenv('google_cloud_project_id')
    df.to_gbq(destination_table = 'ecommerce.fct_orders', project_id=gc_project_id, location='eu-west2')


def transform_report(report_date: str, expected_cols: list[str], id_cols: list[str], date_cols: list[str]):
    
    # df = load_report(report_date)
    df = pd.read_csv('Order_report_2025-02-19.csv')
    df = check_columns(df, expected_cols)
    df = remove_duplicates(df)
    df = check_unique_ids(df, id_cols)
    df = clean_string_columns(df)
    df = clean_date_formats(df, date_cols)
    df = clean_missing_dates(df)
    df = clean_missing_prices(df)
    df = add_line_total_col(df)
    # load_to_bq(df)
