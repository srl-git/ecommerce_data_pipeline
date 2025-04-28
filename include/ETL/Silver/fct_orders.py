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
    report_name = f'order_reports/Order_report_{report_date}.csv'
    bucket = os.getenv('DEST_BUCKET_NAME','')

    try:
        if not gcs.blob_exists(report_name, bucket):
            log.warning(f'No order report dated {report_date} found in {bucket}.')
            raise FileNotFoundError(f'No report found for date {report_date} in bucket {bucket}')
        else:
            return pd.read_csv(f'gcs://{bucket}/{report_name}')
    except Exception as e:
        log.error(f'Error extracting {report_name} from {bucket}: {e}')
        raise
    

def clean_missing_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing item prices firstly using forward/backward fill then by fetching data from Silver.dim_products BigQuery table. 

    Args:
        df (pd.DataFrame): The report DataFrame to transform missing prices.

    Raises:
        ValueError: If no prices are found for the item(s) with missing prices. 

    Returns:
        pd.DataFrame: The transformed report as a DataFrame with missing prices filled in.
    """
    # Fill missing prices from other rows
    df.loc[:, 'item_price'] = df.groupby('item_sku')['item_price'].transform(lambda x: x.ffill().bfill())

    if df.loc[:, 'item_price'].isna().any():
        # Fill missing price from product database
        missing_price_items  = df.loc[:, 'item_sku'][df['item_price'].isnull()].to_list()
        database_prices = bq.run_bq_query(
            f'''
                SELECT item_sku, item_price
                FROM Silver.dim_products
                WHERE item_sku IN UNNEST ({missing_price_items});
            '''
        )
        if database_prices:
            price_dict = {row[0]: row[1] for row in database_prices}
            df['item_price'] = df['item_price'].fillna(df['item_sku'].map(price_dict))
        
        if df.loc[:, 'item_price'].isna().any():
            missing_price_items = df.loc[:, 'item_sku'][df['item_price'].isnull()].to_list()
            raise ValueError(f'The following item_sku values have no item_price values in the report or product database:\n{missing_price_items}')
    return df


def add_line_total_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column in the report DataFrame for the total amount of the order line.

    Args:
        df (pd.DataFrame): The report DataFrame to add the line_total column to.

    Returns:
        pd.DataFrame: The report DataFrame with a line_total column added.
    """
    df = df.assign(line_total=df['qty'] * df['item_price'])
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 7, 6]]
    return df

def add_order_total_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column in the report DataFrame for the total amount of each order.

    Args:
        df (pd.DataFrame): The report DataFrame to add the order_total column to.

    Returns:
        pd.DataFrame: The report DataFrame with an order_total column added.
    """
    df = df.assign(
        order_total=df.groupby('order_id')['line_total'].transform('sum')
    )
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 8, 7]]
    return df

    
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
  
    log.info('Starting validation and transformation on order report.')
    
    try:
        config_file_path = 'ETL/Silver/fct_orders_config.yaml'
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
        df = clean_missing_prices(df)
        df = du.check_ranges(df, **config.get('check_ranges'))
        df = add_line_total_col(df)
        df = add_order_total_col(df)
        df = du.rename_columns(df, **config.get('rename_columns'))
        log.info('Completed validation and transformation on order report.')
        return df
    except Exception as e:
        log.error(f'Error when validating and transforming order report: {e}')
        raise
    

def load_report_to_bq(df: pd.DataFrame) -> None:
    """
    Upsert the report to BigQuery Silver.fct_orders table.

    Args:
        df (pd.DataFrame): The report DataFrame to upsert.
    
    Raises:
        Exception: If an unexpected error occurs during upsert.
    """
    try:
        log.info(f'Uploading report data to BigQuery table Silver.fct_orders.')
        bq.upsert_df_to_bq(
            df=df,
            table='Silver.fct_orders',
            key_col='order_line_id')
    except Exception as e:
        log.error(f'Error writing fct_orders report to BigQuery: {e}')
        raise

def create_silver_table(date: str) -> None:
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
        log.error(f'Error in creating silver table for order report dated {date}: {e}')
        raise