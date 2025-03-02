import pandas as pd
import data_utils as du
import google_cloud_bq_utils as bq


def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    
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
    df = bq.load_df_to_bq(df, 'ecommerce.dim_products')   
    
    return df