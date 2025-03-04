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


def download_df_from_bq(query_or_table : str, project_id: str):

    df = pandas_gbq.read_gbq(query_or_table, project_id)
    return df


def run_bq_query(query: str):

    client = bigquery.Client()
    result = client.query_and_wait(query)
    return result

