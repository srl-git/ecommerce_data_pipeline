from google.cloud import storage
import os
from datetime import datetime
from dotenv import load_dotenv

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


def extract_report(report_name: str, source_bucket: str, dest_bucket: str) -> None:

    if blob_exists(report_name, source_bucket):
        report = download_from_bucket_as_bytes(report_name, source_bucket)
        upload_to_bucket(report_name, report, dest_bucket)
        
        if blob_exists(report_name, dest_bucket):
            print(f'{report_name} downloaded to {dest_bucket}')
    else:
        print(f'{report_name} not found in {source_bucket}')


def main(report_date: str | None =None):

    report_date = datetime.now().strftime('%Y-%m-%d') if report_date is None else report_date
    report_names = [
        f'product_reports/Product_report_{report_date}.csv', 
        f'user_reports/User_report_{report_date}.csv', 
        f'order_reports/Order_report_{report_date}.csv'
    ]
    source_bucket = os.getenv('source_bucket_name','')
    dest_bucket = os.getenv('bucket_name','')
    
    
    for report in report_names:
        extract_report(report, source_bucket, dest_bucket)

load_dotenv()
main()