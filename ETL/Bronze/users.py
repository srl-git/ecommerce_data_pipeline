import pandas as pd
from google.cloud import storage
import os
from dotenv import load_dotenv
load_dotenv()

def blob_exists(blob_name: str, bucket_name: str) -> bool:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()


def upload_to_bucket(blob_name: str, data: bytes, bucket_name: str, content_type: str='text/csv') -> None:
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)

    
def download_from_bucket_as_bytes(blob_name: str, bucket_name: str) -> bytes:

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def extract_report(report_date: str) -> pd.DataFrame | None:

    report_name = f'user_reports/User_report_{report_date}.csv'
    source_bucket = os.getenv('source_bucket_name','')
    dest_bucket = os.getenv('bucket_name','')

    if not blob_exists(report_name, source_bucket):
        print(f'No user report dated {report_date} found in {source_bucket}')
        return
    else:
        report = download_from_bucket_as_bytes(report_name, source_bucket)
        upload_to_bucket(report_name, report, dest_bucket)

        if blob_exists(report_name, dest_bucket):
            print(f'{report_name} downloaded to {dest_bucket}')
    
        return pd.read_csv(f'gcs://{source_bucket}/{report_name}')
