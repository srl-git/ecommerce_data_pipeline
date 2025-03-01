import pandas as pd
import data_utils as du


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
    # df = du.check_outliers(df)
#      # load_to_bq(df)
    
    return df