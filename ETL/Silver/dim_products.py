import pandas as pd
import data_utils as du
import google_cloud_bq_utils as bq
import logger

log = logger.get_logger(__name__)


def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    
    log.info('Starting validation and transformation on product report.')
    try:
        df = du.check_columns(
            df, 
            ['Product SKU', 'Price', 
            'Release Date', 'Date Created', 
            'Date Updated', 'Active']
        )
        df = du.remove_duplicates(df)
        df = du.check_unique(df, ['Product SKU'])
        df = du.clean_strings(df)
        df = du.clean_date_formats(df, ['Date Created', 'Date Updated'])
        df = du.clean_missing_dates(df)
        df = du.check_positive(df)
        df = du.rename_columns(
            df,
            {'Product SKU': 'item_sku',
            'Price': 'item_price',
            'Release Date': 'item_release_date',
            'Date Created': 'item_creation_date', 
            'Date Updated': 'item_updated_date',
            'Active': 'item_active'}
        )
        # df = du.check_outliers(df)
        return df
    except Exception as e:
        log.error(f'Error when validating and transforming product report: {e}')
        return None
    

def create_silver_table(df: pd.DataFrame | None) -> None:
    
    if df is None:
        return None
    try:
        log.info(f'Uploading report data to bigquery table Silver.dim_products.')
        bq.load_df_to_bq(df, 'Silver.dim_products')
    except Exception as e:
        log.error(f'Error writing dim_products report to bigquery: {e}')