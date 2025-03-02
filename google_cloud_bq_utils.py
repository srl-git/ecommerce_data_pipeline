from google.cloud import bigquery
import pandas as pd
import pandas_gbq


def load_df_to_bq(df: pd.DataFrame, table: str) -> pd.DataFrame:

    if df is None:
        return
    
    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=table,
        if_exists='append',
        location='europe-west2'
    )
    return df

client = bigquery.Client()
