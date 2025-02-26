import os
from dotenv import load_dotenv
import google_cloud_storage_utils as gcs

load_dotenv()

def extract_report(report_date: str):

    report_name = f'product_reports/Product_report_{report_date}.csv'
    source_bucket_name = os.getenv('source_bucket_name')
    dest_bucket_name = os.getenv('dest_bucket_name')

    if gcs.check_file_exists(report_name, source_bucket_name):
        report = gcs.download_from_bucket_as_bytes(report_name, source_bucket_name)
        gcs.upload_to_bucket(report_name, report, dest_bucket_name)
    else:
        print(f'{report_name} not found in {source_bucket_name}')

    if gcs.check_file_exists(report_name, dest_bucket_name):
        print(f'{report_name} downloaded to {dest_bucket_name}')
    