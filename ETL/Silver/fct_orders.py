import pandas as pd
import yaml

import utils.data_utils as du
import utils.google_cloud_bq_utils as bq
import utils.logger as logger

log = logger.get_logger(__name__)


def clean_missing_prices(df: pd.DataFrame) -> pd.DataFrame:

    # Fill missing prices from other rows
    df.loc[:, 'item_price'] = df.groupby('item_sku')['item_price'].transform(lambda x: x.ffill().bfill())

    if df.loc[:, 'item_price'].isna().any():
        # Fill missing price from product database
        missing_price_items  = df.loc[:, 'item_sku'][df['item_price'].isnull()].to_list()
        database_prices = bq.run_bq_query(
            f'''
                SELECT item_sku, item_price
                FROM ecommerce.dim_products
                WHERE item_sku IN UNNEST ({missing_price_items});
            '''
        )
        price_dict = {row[0]: row[1] for row in database_prices}
        df['item_price'] = df['item_price'].fillna(df['item_sku'].map(price_dict))
        if df.loc[:, 'item_price'].isna().any():
            missing_price_items = df.loc[:, 'item_sku'][df['item_price'].isnull()].to_list()
            raise ValueError(f'The following item_sku values have no item_price values in the report or product database:\n{missing_price_items}')
    return df


def add_line_total_col(df: pd.DataFrame) -> pd.DataFrame:

    df = df.assign(line_total=df['qty'] * df['item_price'])
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 7, 6]]
    return df

    
def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    
    log.info('Starting validation and transformation on order report.')
    try:
        with open('ETL/Silver/fct_orders_config.yaml', 'rt') as f:
            config = yaml.safe_load(f.read())
        df = du.check_columns(df, **config.get('check_columns'))
        df = du.remove_duplicates(df)
        df = du.check_unique(df, **config.get('check_unique'))
        df = du.clean_strings(df)
        df = du.clean_date_formats(df, **config.get('clean_date_formats'))
        df = du.clean_missing_dates(df)
        df = clean_missing_prices(df)
        df = du.check_ranges(df, **config.get('check_ranges'))
        df = add_line_total_col(df)
        df = du.rename_columns(df, **config.get('rename_columns'))
        log.info('Completed validation and transformation on order report.')
        return df
    except Exception as e:
        log.error(f'Error when validating and transforming order report: {e}')
        return None
    

def create_silver_table(df: pd.DataFrame | None) -> None:
    
    if df is None:
        return None
    try:
        log.info(f'Uploading report data to biquery table Silver.fct_orders.')
        bq.load_df_to_bq(df, 'Silver.fct_orders')   
    except Exception as e:
        log.error(f'Error writing fct_orders report to BigQuery: {e}')