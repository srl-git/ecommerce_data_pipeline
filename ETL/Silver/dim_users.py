import pandas as pd
import data_utils as du


def validate_and_transform_report(df: pd.DataFrame | None) -> pd.DataFrame | None:
    
    if df is None:
        return
    
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
    # df = du.check_outliers(df)
#      # load_to_bq(df)
    
    return df