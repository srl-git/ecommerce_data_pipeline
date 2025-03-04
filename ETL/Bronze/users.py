import pandas as pd
from google.cloud import storage
import os
from dotenv import load_dotenv
import google_cloud_storage_utils as gcs

load_dotenv()


def extract_report(report_date: str) -> pd.DataFrame | None:

    report_name = f'user_reports/User_report_{report_date}.csv'
    source_bucket = os.getenv('source_bucket_name','')

    if not gcs.blob_exists(report_name, source_bucket):
        print(f'No user report dated {report_date} found in {source_bucket}')
        return
    else:
        return pd.read_csv(f'gcs://{source_bucket}/{report_name}')


def save_df_to_cloud_storage(report_date: str, df: pd.DataFrame | None) -> pd.DataFrame | None:

    if df is None:
        return
    
    report_name = f'user_reports/User_report_{report_date}.csv'
    dest_bucket = os.getenv('bucket_name','')
    gcs.upload_to_bucket(report_name, df.to_csv(index=False), dest_bucket)
    return df

def extract_and_save_report(report_date: str) -> pd.DataFrame | None:
    
    df = extract_report(report_date)
    df = save_df_to_cloud_storage(report_date, df)
    return df