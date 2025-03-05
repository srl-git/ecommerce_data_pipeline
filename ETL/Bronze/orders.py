import os
import pandas as pd
from dotenv import load_dotenv
import logger
import google_cloud_storage_utils as gcs

load_dotenv()

log = logger.get_logger(__name__)


def extract_report(report_date: str) -> pd.DataFrame | None:

    report_name = f'order_reports/Order_report_{report_date}.csv'
    source_bucket = os.getenv('source_bucket_name','')

    try:
        if not gcs.blob_exists(report_name, source_bucket):
            log.warning(f'No order report dated {report_date} found in {source_bucket}.')
            return None
        else:
            log.info(f'Order report dated {report_date} extracted from {source_bucket}.')
            return pd.read_csv(f'gcs://{source_bucket}/{report_name}')
    except Exception as e:
        log.error(f'Error extracting {report_name} from {source_bucket}: {e}')
        return None

def save_df_to_cloud_storage(report_date: str, df: pd.DataFrame | None) -> pd.DataFrame | None:

    if df is None:
        return None
    
    report_name = f'order_reports/Order_report_{report_date}.csv'
    dest_bucket = os.getenv('bucket_name','')
    try:
        gcs.upload_to_bucket(report_name, df.to_csv(index=False), dest_bucket)
        log.info(f'Order report dated {report_date} saved to {dest_bucket}.')
        return df
    except Exception as e:
        log.error(f'Error saving order report to {dest_bucket}: {e}')
        return None
    

def extract_and_save_report(report_date: str) -> pd.DataFrame | None:
    
    try:
        df = extract_report(report_date)
        if df is not None:
            df = save_df_to_cloud_storage(report_date, df)
        return df
    except Exception as e:
        log.error(f'Error in extract_and_save_report for order report dated {report_date}: {e}')
        return None