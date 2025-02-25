from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from google_cloud_storage import list_bucket_contents, download_from_bucket, download_from_bucket_as_bytes

load_dotenv()

# today = datetime.now().strftime('%Y-%m-%d')
# bucket_name = os.getenv('bucket_name')
# todays_reports = [blob.name for blob in list_bucket_contents(bucket_name) if '2025-02-20' in blob.name]

# for report in todays_reports:
#     if 'Order_report' in report:
#         # download_from_bucket(report, bucket_name, 'test.csv')
#         file = download_from_bucket_as_bytes(report, bucket_name)
#         for row in file:
#             if row < 30:
#                 print(row)


expected_cols = ['order_line_id', 'order_id', 'user_id', 'item_sku', 'qty', 'item_price', 'date_created']

df = pd.read_csv('Order_report_2025-02-19-2.csv')

prices = {'SUMO005': 21, 'GAS006': 20}


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


df = check_columns(df, expected_cols)
df = remove_duplicates(df)
df = clean_string_columns(df)
df = clean_date_formats(df, 'date_created')
df = clean_missing_dates(df)
df = clean_missing_prices(df)
# df.to_csv('export.csv',index=False)
# print(df.isna().sum())
# print(df.tail(50))

        