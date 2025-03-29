from google.cloud import bigquery
import pandas as pd
import pandas_gbq
# import utils.logger as logger

# log = logger.get_logger(__name__)


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


def upsert_df_to_bq(df: pd.DataFrame, table: str, key_col: str) -> pd.DataFrame:
    
    client = bigquery.Client()
    staging_table = f'{table}_staging'

    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=staging_table,
        if_exists='replace',
        location='europe-west2'
    )

    cols = [col for col in df.columns]
    update_set_clause = ',\n'.join(f'T.{col} = S.{col}' for col in cols)
    insert_cols = ', '.join(cols)
    insert_vals = ', '.join(f'S.{col}' for col in cols)

    merge_query = f'''
        MERGE INTO `{table}` T
        USING `{staging_table}` S
        ON T.{key_col} = S.{key_col}
        WHEN MATCHED THEN
            UPDATE SET 
            {update_set_clause}
        WHEN NOT MATCHED THEN
            INSERT ({insert_cols}) VALUES ({insert_vals})
        '''

    query_job = client.query(merge_query)
    query_job.result()
    client.delete_table(staging_table, not_found_ok=True)

    return df


def download_df_from_bq(query_or_table : str, project_id: str):

    df = pandas_gbq.read_gbq(query_or_table, project_id)
    return df


def run_bq_query(query: str):

    client = bigquery.Client()
    result = client.query_and_wait(query)
    return result
