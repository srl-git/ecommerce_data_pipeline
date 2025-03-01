import os
from dotenv import load_dotenv
import google_cloud_storage_utils as gcs

load_dotenv()


def extract_report(report_date: str) -> None:

    report_name = f'user_reports/User_report_{report_date}.csv'
    source_bucket = os.getenv('source_bucket_name')
    dest_bucket = os.getenv('bucket_name')

    if gcs.blob_exists(report_name, source_bucket):
        report = gcs.download_from_bucket_as_bytes(report_name, source_bucket)
        gcs.upload_to_bucket(report_name, report, dest_bucket)
        
        if gcs.blob_exists(report_name, dest_bucket):
            print(f'{report_name} downloaded to {dest_bucket}')
    else:
        print(f'{report_name} not found in {source_bucket}')