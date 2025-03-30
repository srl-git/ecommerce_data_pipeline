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


def extract_report(report_date: str) -> pd.DataFrame | None:

    report_name = f'product_reports/Product_report_{report_date}.csv'
    bucket = os.getenv('bucket_name','')

    try:
        if not gcs.blob_exists(report_name, bucket):
            log.warning(f'No product report dated {report_date} found in {bucket}.')
            return None
        else:
            return pd.read_csv(f'gcs://{bucket}/{report_name}')
    except Exception as e:
        log.error(f'Error extracting {report_name} from {bucket}: {e}')
        return None


def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    log.info('Starting validation and transformation on product report.')
    
    try:
        with open('ETL/Silver/dim_products_config.yaml', 'rt') as f:
            config = yaml.safe_load(f.read())
        df = du.check_columns(df, **config.get('check_columns')) 
        df = du.remove_duplicates(df)
        df = du.check_unique(df, **config.get('check_unique'))
        df = du.clean_strings(df)
        df = du.clean_date_formats(df, **config.get('clean_date_formats'))
        df = du.clean_missing_dates(df)
        df = du.check_ranges(df, **config.get('check_ranges'))
        df = du.rename_columns(df, **config.get('rename_columns'))
        log.info('Completed validation and transformation on product report.')
        return df
    except Exception as e:
        log.error(f'Error when validating and transforming product report: {e}')
        return None


def load_report_to_bq(df: pd.DataFrame | None) -> None:

    if df is None:
        return None
    log.info(f'Uploading report data to BigQuery table Silver.dim_products.')

    try:
        bq.upsert_df_to_bq(
            df=df,
            table='Silver.dim_products',
            key_col='item_sku')
    except Exception as e:
        log.error(f'Error writing dim_products report to BigQuery: {e}')


def create_silver_table(date: str) -> None:
    
    report = extract_report(date)
    transformed_report = validate_and_transform_report(report)
    load_report_to_bq(transformed_report)
