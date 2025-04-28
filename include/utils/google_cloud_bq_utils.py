from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator
from google.cloud.exceptions import NotFound
import pandas as pd
import pandas_gbq


def load_df_to_bq(df: pd.DataFrame, table: str, replace = False) -> None:
    """
    Load a DataFrame into a BigQuery table.

    This function loads a given DataFrame into a specified BigQuery table.
    If replace is True, the table will be truncated before loading the data.

    Args:
        df (pd.DataFrame): The DataFrame to load into BigQuery.
        table (str): The destination BigQuery table where the data will be loaded.
        replace (bool): Whether to replace the table (True) or append to it (False). Default is False.

    Returns:
        None
    """
    if df is None:
        return
    
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        write_disposition='WRITE_TRUNCATE' if replace else 'WRITE_APPEND',
    )
    job = client.load_table_from_dataframe(
        dataframe=df,
        destination=table,
        job_config=job_config
    )
    job.result()
    return


def upsert_df_to_bq(df: pd.DataFrame, table: str, key_col: str) -> None:
    """
    Upsert a DataFrame into a BigQuery table.

    This function performs an upsert operation on the specified BigQuery table.
    It first loads the DataFrame into a staging table, then performs a merge operation
    to insert or update data in the destination table based on the given key column.

    Args:
        df (pd.DataFrame): The DataFrame to upsert into BigQuery.
        table (str): The destination BigQuery table where the data will be upserted.
        key_col (str): The column to be used as the key for matching records during the upsert.

    Returns:
        None
    """
    if df is None:
        return
    
    client = bigquery.Client()
    staging_table = f'{table}_staging'
    load_df_to_bq(df, staging_table, replace=True)

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
    return


def download_df_from_bq(query_or_table : str) -> pd.DataFrame | None:
    """
    Download data from BigQuery into a pandas DataFrame.

    This function downloads data either from a BigQuery table or by running a query
    and returning the result as a pandas DataFrame.

    Args:
        query_or_table (str): Either a BigQuery SQL query or the name of a BigQuery table to retrieve data from.
        project_id (str): The GCP project ID for the BigQuery operation.

    Returns:
        pd.DataFrame | None: A pandas DataFrame containing the query results or None if no results.
    """
    df = pandas_gbq.read_gbq(query_or_table)
    return df


def run_bq_query(query: str) -> RowIterator | None:
    """
    Run a BigQuery query and return the result as a RowIterator.

    Args:
        query (str): The BigQuery SQL query to run.

    Returns:
        RowIterator | None: A RowIterator containing the query result rows, or None if the query fails.
    """
    client = bigquery.Client()
    result = client.query_and_wait(query)
    return result

def check_table_exists(table: str) -> bool:
    """
    Check if a BigQuery table exists.

    Args:
        table (str): The name of the BigQuery table to check.

    Returns:
        bool: True if the table exists, False if the table does not exist.
    """
    client = bigquery.Client()
    try:
        client.get_table(table)
        return True
    except NotFound:
        return False
    