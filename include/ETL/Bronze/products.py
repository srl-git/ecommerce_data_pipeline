import os
import requests

import pandas as pd
from dotenv import load_dotenv

import utils.logger as logger
import utils.google_cloud_storage_utils as gcs
from utils.google_cloud_auth import get_identity_token

load_dotenv()

log = logger.get_logger(__name__)

def extract_report(report_date: str) -> pd.DataFrame | None:
    """
    Extract the CSV report for a given date from Google Cloud Storage.

    Args:
        report_date (str): The date of the report to extract in the YYYY-MM-DD format.

    Raises:
        Exception: If an unexpected error occurs during extraction.

    Returns:
        pd.DataFrame | None: The extracted report as a DataFrame or None if the report does not exist.
    """
    report_name = f'product_reports/Product_report_{report_date}.csv'
    source_bucket = os.getenv('SOURCE_BUCKET_NAME','')

    try:
        if not gcs.blob_exists(report_name, source_bucket):
            log.warning(f'No product report dated {report_date} found in {source_bucket}.')
            return None
        else:
            log.info(f'Product report dated {report_date} extracted from {source_bucket}.')
            return pd.read_csv(f'gcs://{source_bucket}/{report_name}')
    except Exception as e:
        log.error(f'Error extracting {report_name} from {source_bucket}: {e}')
        raise


def extract_report_from_api(report_date: str) -> pd.DataFrame | None:
    """
    Extract product data for a given date from an API.

    Args:
        report_date (str): The date of the report to extract in the YYYY-MM-DD format.

    Raises:
        ConnectionError: If an error occurs while connecting to the API or receiving a server error.
        Exception: If an unexpected error occurs during extraction.

    Returns:
        pd.DataFrame | None: The extracted report as a DataFrame, or None if no data is available for the date.
    """
    try:
        api_end_point = os.getenv('API_END_POINT')
        url = f'{api_end_point}/products?date_updated={report_date}'

        identity_token = get_identity_token()
        auth_header = {"Authorization": "Bearer " + identity_token}

        response = requests.get(url, headers=auth_header)
        match response.status_code:
            case 200:
                data = response.json()
                return pd.DataFrame.from_dict(data)
            case 404:
                log.warning(f'No product data for {report_date}: {response.status_code}, {response.text}')
                return None
            case 500:
                log.error(f'Error fetching Product data: {response.status_code}, {response.text}')
                raise ConnectionError
            case _:
                log.error(f'Error fetching Product data: {response.status_code}, {response.text}')
                raise ConnectionError
    except Exception as e:
        log.error(f'Error fetching Product report: {e}')
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
    report_name = f'product_reports/Product_report_{report_date}.csv'
    dest_bucket = os.getenv('DEST_BUCKET_NAME','')
    try:
        if gcs.blob_exists(report_name, dest_bucket):
            log.warning(f'Product report dated {report_date} already exists in {dest_bucket}.')
            return df
        else:
            gcs.upload_to_bucket(report_name, df.to_csv(index=False), dest_bucket)
            log.info(f'Product report dated {report_date} saved to {dest_bucket}.')
            return df
    except Exception as e:
        log.error(f'Error saving product report to {dest_bucket}: {e}')
        raise


def extract_and_save_report(report_date: str) -> pd.DataFrame | None:
    """
    Extract the report for a given date from an API and upload it to Google Cloud Storage.

    Args:
        report_date (str): The date of the report to extract and save in YYYY-MM-DD format.

    Raises:
        Exception: If an error occurs during extraction or upload.

    Returns:
        pd.DataFrame: The extracted and saved report DataFrame.
    """
    try:
        # df = extract_report(report_date)
        df = extract_report_from_api(report_date)
        if df is not None:
            df = save_df_to_cloud_storage(report_date, df)
        return df
    except Exception as e:
        log.error(f'Error in extract_and_save_report for product report dated {report_date}: {e}')
        raise
    