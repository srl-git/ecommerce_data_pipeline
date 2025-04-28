import os

from dotenv import load_dotenv
import pandas as pd
import yaml

import utils.data_utils as du
import utils.google_cloud_storage_utils as gcs
import utils.google_cloud_bq_utils as bq
import utils.logger as logger


load_dotenv()

log = logger.get_logger(__name__)


def extract_report(report_date: str) -> pd.DataFrame:
    """
    Extract the report for a given date from Bronze layer storage.

    Args:
        report_date (str): The date of the report to extract in YYYY-MM-DD format.

    Returns:
        pd.DataFrame: The extracted report as a DataFrame.
    
    Raises:
        FileNotFoundError: If no report exists for the given date.
        Exception: If an unexpected error occurs during extraction.
    """
    report_name = f'user_reports/User_report_{report_date}.csv'
    bucket = os.getenv('DEST_BUCKET_NAME','')

    try:
        if not gcs.blob_exists(report_name, bucket):
            log.warning(f'No user report dated {report_date} found in {bucket}.')
            raise FileNotFoundError(f'No report found for date {report_date} in bucket {bucket}')
        else:
            log.info(f'User report dated {report_date} extracted from {bucket}.')
            return pd.read_csv(f'gcs://{bucket}/{report_name}')
    except Exception as e:
        log.error(f'Error extracting {report_name} from {bucket}: {e}')
        raise
    

def validate_and_transform_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and transform the data in the report DataFrame.

    Args:
        df (pd.DataFrame): The report DataFrame to validate and transform.

    Raises:
        Exception: If an error occurs during validation or transformation.
    
    Returns:
        pd.DataFrame: The validated and transformed report as a DataFrame.
    """
    log.info('Starting validation and transformation on user report.')
    
    try:
        config_file_path = 'ETL/Silver/dim_users_config.yaml'
        if os.getenv('AIRFLOW_HOME'):
            config_file_path = f'/opt/airflow/include/{config_file_path}'
        with open(config_file_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        df = du.check_columns(df, **config.get('check_columns')) 
        df = du.remove_duplicates(df)
        df = du.check_unique(df, **config.get('check_unique'))
        df = du.clean_strings(df)
        df = du.clean_date_formats(df, **config.get('clean_date_formats'))
        df = du.clean_missing_dates(df)
        df = du.rename_columns(df, **config.get('rename_columns'))
        log.info('Completed validation and transformation on user report.')
        return df
    except Exception as e:
        log.error(f'Error when validating and transforming user report: {e}')
        raise


def load_report_to_bq(df: pd.DataFrame) -> None:
    """
    Upsert the report to BigQuery Silver.dim_users table.

    Args:
        df (pd.DataFrame): The report DataFrame to upsert.
    
    Raises:
        Exception: If an unexpected error occurs during upsert.
    """
    log.info(f'Uploading transformed user report data to BigQuery table Silver.dim_users.')
    
    try:
        bq.upsert_df_to_bq(
            df=df,
            table='Silver.dim_users',
            key_col='user_id')
    except Exception as e:
        log.error(f'Error writing dim_users report to BigQuery: {e}')
        raise

def create_silver_table(date:str) -> None:
    """
    Extract the report for a given date from Bronze layer storage, validate and transform the data and upsert to BigQuery.

    Args:
        date (str): The date of the report in YYYY-MM-DD format.
    
    Raises:
        Exception: If an error occurs during extraction, validation, transformation or upload.
    """
    try: 
        report = extract_report(date)
        transformed_report = validate_and_transform_report(report)
        load_report_to_bq(transformed_report)
    except Exception as e:
        log.error(f'Error in creating silver table for user report dated {date}: {e}')
        raise
