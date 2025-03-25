import pandas as pd
import yaml

import utils.data_utils as du
import utils.google_cloud_bq_utils as bq
import utils.logger as logger

log = logger.get_logger(__name__)


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
    

def create_silver_table(df: pd.DataFrame | None) -> None:
    
    if df is None:
        return None
    try:
        log.info(f'Uploading report data to BigQuery table Silver.dim_products.')
        bq.load_df_to_bq(df, 'Silver.dim_products')
    except Exception as e:
        log.error(f'Error writing dim_products report to BigQuery: {e}')