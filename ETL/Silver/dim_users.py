import pandas as pd
import data_utils as du
import google_cloud_bq_utils as bq
import logger

log = logger.get_logger(__name__)


def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    
    log.info('Starting validation and transformation on user report.')
    try:
        df = du.check_columns(
            df,
            ['user_id',	'user_name',
            'user_address',	'user_country',
            'user_email', 'date_created']
        )
        df = du.remove_duplicates(df)
        df = du.check_unique(df, ['user_id'])
        df = du.clean_strings(df)
        df = du.clean_date_formats(df, ['date_created'])
        df = du.clean_missing_dates(df)
        df = du.rename_columns(df, {'date_created': 'user_date_created'})
        # df = du.check_outliers(df)
        log.info(f'Uploading report data to biquery table ecommerce.dim_users.')
        df = bq.load_df_to_bq(df, 'ecommerce.dim_users')   
        return df
    except Exception as e:
        log.error(f'Error when validating and transfroming user report: {e}')
        return None