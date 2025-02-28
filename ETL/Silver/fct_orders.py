import os
from dotenv import load_dotenv
import pandas as pd
import google_cloud_storage_utils as gcs

prices = {'SUMO005': 21, 'GAS006': 20}

expected_cols = ['order_line_id', 'order_id', 'user_id', 'item_sku', 'qty', 'item_price', 'date_created']

def load_report(report_date: str) -> pd.DataFrame:

    bucket_name = os.getenv('bucket_name')
    report_name = f'order_reports/Order_report_{report_date}.csv'
    df = pd.read_csv(f'gcs://{bucket_name}/{report_name}')
    return df


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

    df = df.drop_duplicates(keep='first')
    return df


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame: 

    for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
    return df


def clean_date_formats(df: pd.DataFrame, date_column: str | list[str]) -> pd.DataFrame:

    date_column = [date_column] if isinstance(date_column, str) else date_column
    for col in date_column:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed', dayfirst=True,)
    return df


def clean_missing_dates(df: pd.DataFrame) -> pd.DataFrame:

    for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        df[col] = df[col].ffill().bfill()
    return df


def clean_missing_prices(df: pd.DataFrame) -> pd.DataFrame:

    df['item_price'] = df.groupby('item_sku')['item_price'].transform(lambda x: x.ffill().bfill()) # fill price from other rows
    df['item_price'] = df['item_price'].fillna(df['item_sku'].map(prices)) # fill price from database as dict
    return df

def validate_and_clean(report_date: str):

    df = load_report(report_date)
    df = check_columns(df, expected_cols)
    df = remove_duplicates(df)
    df = clean_string_columns(df)
    df = clean_date_formats(df, 'date_created')
    df = clean_missing_dates(df)
    df = clean_missing_prices(df)

    return df


# df.to_csv('export.csv',index=False)
# print(df.isna().sum())
# print(df.tail(50))