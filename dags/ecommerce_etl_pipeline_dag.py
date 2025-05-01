import os
from datetime import timedelta

from airflow.decorators import dag, task, task_group
from pendulum import datetime

from utils.airflow_notification import notify_task_state


default_args = {
    'owner': 'Sam RL',
    'depends_on_past': True,
    'start_date': datetime(2025, 4, 12),
    'catchup': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=20),
    'email_on_success': True,
    'email_on_failure': True,
    'email': [os.getenv('EMAIL')],
    'on_failure_callback': notify_task_state,
    'on_retry_callback': notify_task_state
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
        """
        Extract raw data from API/CSV reports and store in Google Cloud Storage.
        """
        @task
        def extract_products_task(ds):
            from ETL.Bronze import products
            products.extract_and_save_report(ds)

        @task
        def extract_users_task(ds):
            from ETL.Bronze import users
            users.extract_and_save_report(ds)

        @task
        def extract_orders_task(ds):
            from ETL.Bronze import orders
            orders.extract_and_save_report(ds)

        extract_products_task() >> extract_users_task() >> extract_orders_task()
    

    @task_group
    def transform():
        """
        Vaildate/transform raw data and load to BigQuery silver tables.
        """
        @task
        def transform_products_task(ds):
            from ETL.Silver import dim_products
            dim_products.create_silver_table(ds)

        @task
        def transform_users_task(ds):
            from ETL.Silver import dim_users
            dim_users.create_silver_table(ds)

        @task
        def transform_orders_task(ds):
            from ETL.Silver import fct_orders
            fct_orders.create_silver_table(ds)
   
        transform_products_task() >> transform_users_task() >> transform_orders_task()


    @task_group
    def load():
        """
        Aggregate/join data and load to BigQuery gold tables.
        """
        @task
        def load_obt_task(ds):
            from ETL.Gold import obt
            obt.create_gold_table(ds)

        @task
        def load_user_metrics_task():
            from ETL.Gold import user_metrics
            user_metrics.create_gold_table()

        @task
        def load_product_metrics_task():
            from ETL.Gold import product_metrics
            product_metrics.create_gold_table()

        @task
        def load_daily_sales_report_task():
            from ETL.Gold import daily_sales_report
            daily_sales_report.create_gold_table()

        load_obt_task() >> load_user_metrics_task() >> load_product_metrics_task() >> load_daily_sales_report_task()

    @task
    def send_daily_report_task():
        from ETL.Gold import daily_sales_report
        to_emails = [os.getenv('EMAIL','')]
        daily_sales_report.send_daily_sales_report(to_emails)

    extract() >> transform() >> load() >> send_daily_report_task()


ecommerce_ETL_pipeline()