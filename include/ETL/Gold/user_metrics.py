import utils.google_cloud_bq_utils as bq
import utils.logger as logger


log = logger.get_logger(__name__)


def create_gold_table() -> None:
    
    log.info('Creating user metrics on BigQuery table Gold.user_metrics.')
    try:
        bq.run_bq_query(f'''
                CREATE OR REPLACE TABLE Gold.user_metrics AS
                WITH user_orders AS (
                    SELECT
                        user_id,
                        user_name,
                        user_country,
                        COUNT(DISTINCT order_id) AS total_orders,
                        SUM(line_total) AS total_spent,
                        SAFE_DIVIDE(SUM(line_total), COUNT(DISTINCT order_id)) AS avg_order_value,
                        MIN(order_date_created) AS first_order_date,
                        MAX(order_date_created) AS last_order_date
                    FROM `Gold.obt`
                    GROUP BY 
                        user_id,
                        user_name,
                        user_country
                )
                SELECT * 
                FROM user_orders
                ORDER BY total_spent DESC;
                '''
        )
    except Exception as e:
        log.error(f'Error while creating user metrics table in BigQuery: {e}')

create_gold_table()