import pandas as pd
import data_utils as du
import google_cloud_bq_utils as bq


def clean_missing_prices(df: pd.DataFrame) -> pd.DataFrame:
    df['item_price'] = df.groupby('item_sku')['item_price'].transform(lambda x: x.ffill().bfill()) # fill price from other rows
    # df['item_price'] = df['item_price'].fillna(df['item_sku'].map(prices)) # fill price from database as dict
    return df


def add_line_total_col(df: pd.DataFrame) -> pd.DataFrame:

    df['line_total'] = df['qty'] * df['item_price']
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 7, 6]]
    return df

    
def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    
    df = du.check_columns(
        df, 
        ['order_line_id', 'order_id', 
        'user_id', 'item_sku', 'qty', 
        'item_price', 'date_created']
    )
    df = du.remove_duplicates(df)
    df = du.check_unique(df, ['order_line_id'])
    df = du.clean_strings(df)
    df = du.clean_date_formats(df, ['date_created'])
    df = du.clean_missing_dates(df)
    df = clean_missing_prices(df)
    df = du.check_positive(df, ['order_line_id'])
    df = add_line_total_col(df)
    df = du.rename_columns(
        df, 
        {'item_price': 'order_item_price',
        'date_created': 'order_date_created'}
    )
    # df = du.check_outliers(df)
    df = bq.load_df_to_bq(df, 'ecommerce.fct_orders')   
    return df
 
