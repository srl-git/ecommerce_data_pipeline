import os

import pandas as pd
from dotenv import load_dotenv

import utils.logger as logger
import utils.google_cloud_storage_utils as gcs

load_dotenv()

log = logger.get_logger(__name__)


def extract_report(report_date: str) -> pd.DataFrame:
    """
    Extract the CSV report for a given date from Google Cloud Storage.

    Args:
        report_date (str): The date of the report to extract in the YYYY-MM-DD format.

    Raises:
        FileNotFoundError: If no CSV report exists for the given date.
        Exception: If an unexpected error occurs during extraction.

    Returns:
        pd.DataFrame: The extracted report as a DataFrame.
    """
    report_name = f'order_reports/Order_report_{report_date}.csv'
    source_bucket = os.getenv('SOURCE_BUCKET_NAME','')
    try:
        if not gcs.blob_exists(report_name, source_bucket):
            log.warning(f'No order report dated {report_date} found in {source_bucket}.')
            raise FileNotFoundError
        else:
            log.info(f'Order report dated {report_date} extracted from {source_bucket}.')
            return pd.read_csv(f'gcs://{source_bucket}/{report_name}')
    except Exception as e:
        log.error(f'Error extracting {report_name} from {source_bucket}: {e}')
        raise


def save_df_to_cloud_storage(report_date: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Upload the report DataFrame to Google Cloud Storage.

    Args:
        report_date (str): The date of the report to save in YYYY-MM-DD format.
        df (pd.DataFrame): The report DataFrame to upload to Google Cloud Storage.

    Raises:
        Exception: If an unexpected error occurs during upload.

    Returns:
        pd.DataFrame: The report DataFrame.
    """    
    report_name = f'order_reports/Order_report_{report_date}.csv'
    dest_bucket = os.getenv('DEST_BUCKET_NAME','')
    try:
        if gcs.blob_exists(report_name, dest_bucket):
            log.warning(f'Order report dated {report_date} already exists in {dest_bucket}.')
            return df
        else:
            gcs.upload_to_bucket(report_name, df.to_csv(index=False), dest_bucket)
            log.info(f'Order report dated {report_date} saved to {dest_bucket}.')
            return df
    except Exception as e:
        log.error(f'Error saving order report to {dest_bucket}: {e}')
        raise
    

def extract_and_save_report(report_date: str) -> pd.DataFrame:
    """
    Extract the report for a given date from Google Cloud Storage and upload it to another storage bucket.

    Args:
        report_date (str): The date of the report to extract and save in YYYY-MM-DD format.

    Raises:
        Exception: If an error occurs during extraction or upload.

    Returns:
        pd.DataFrame: The extracted and saved report DataFrame.
    """
    try:
        df = extract_report(report_date)
        df = save_df_to_cloud_storage(report_date, df)
        return df
    except Exception as e:
        log.error(f'Error in extract_and_save_report for order report dated {report_date}: {e}')
        raise