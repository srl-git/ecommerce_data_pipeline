import google_cloud_bq_utils as bq
import logger

log = logger.get_logger(__name__)


def create_gold_table():
    
    log.info('Creating/updating user metrics on bigquery table Gold.user_metrics.')
    try:
        bq.run_bq_query(f'''
                CREATE OR REPLACE TABLE Gold.user_metrics AS
                SELECT
                    user_id,
                    user_name,
                    user_country,
                    SUM(line_total) / COUNT(DISTINCT order_id) AS avg_spend,
                    COUNT(DISTINCT(order_id)) AS total_orders,
                    SUM(line_total) AS total_spend,
                    MAX(order_date_created) AS last_order_date
                FROM `Gold.obt`
                GROUP BY 
                    user_id,
                    user_name,
                    user_country
                ORDER BY total_spend DESC;
            '''
        )
    except Exception as e:
        log.error(f'Error while creating user metrics table in bigquery: {e}')
