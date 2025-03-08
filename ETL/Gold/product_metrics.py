import google_cloud_bq_utils as bq
import logger

log = logger.get_logger(__name__)


def create_gold_table():
    
    log.info('Creating/updating product metrics on BigQuery table Gold.product_metrics.')
    try:
        bq.run_bq_query(f'''
                CREATE OR REPLACE TABLE Gold.product_metrics AS
                SELECT
                    item_sku,
                    SUM(qty) AS total_sold,
                    SUM(line_total) AS total_revenue,
                    MAX(order_date_created) AS last_order_date
                FROM `Gold.obt`
                GROUP BY item_sku
                ORDER BY total_revenue DESC;
            '''
        )
    except Exception as e:
        log.error(f'Error while creating product metrics table in BigQuery: {e}')    