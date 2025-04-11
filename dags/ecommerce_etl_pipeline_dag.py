from datetime import timedelta

from airflow.decorators import dag, task, task_group
from pendulum import datetime

from ETL.Bronze import products, users, orders
from ETL.Silver import fct_orders, dim_products, dim_users
from ETL.Gold import obt, user_metrics, product_metrics


default_args = {
    'owner': 'Sam RL',
    'depends_on_past': True,
    'start_date': datetime(2025, 4, 10),
    'catchup': False,
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=20)
}

@dag(
    dag_id='Ecommerce_ETL_Pipeline',
    tags=['ecommerce'],
    max_active_runs=1,
    schedule_interval='@daily',
    default_args=default_args
)
def ecommerce_ETL_pipeline():
    
    @task_group
    def extract():

        @task
        def extract_products_task(ds):
            products.extract_and_save_report(ds)

        @task
        def extract_users_task(ds):
            users.extract_and_save_report(ds)

        @task
        def extract_orders_task(ds):
            orders.extract_and_save_report(ds)

        extract_products_task() >> extract_users_task() >> extract_orders_task()
    
    @task_group
    def transform():

        @task
        def transform_products_task(ds):
            dim_products.create_silver_table(ds)

        @task
        def transform_users_task(ds):
            dim_users.create_silver_table(ds)

        @task
        def transform_orders_task(ds):
            fct_orders.create_silver_table(ds)
   
        transform_products_task() >> transform_users_task() >> transform_orders_task()


    @task_group
    def load():

        @task
        def load_obt_task(ds):
            obt.create_gold_table(ds)

        load_obt_task()


    extract() >> transform() >> load()

    
ecommerce_ETL_pipeline()
