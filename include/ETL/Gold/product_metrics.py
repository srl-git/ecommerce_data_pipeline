import utils.google_cloud_bq_utils as bq
import utils.logger as logger


log = logger.get_logger(__name__)


def create_gold_table() -> None:
    
    log.info('Creating product metrics on BigQuery table Gold.product_metrics.')
    try:
        bq.run_bq_query(f'''
                DECLARE yesterday DATE DEFAULT DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY);
                CREATE OR REPLACE TABLE Gold.product_metrics AS
                WITH product_metrics AS (
                SELECT
                        item_sku,
                        SUM(qty) AS total_qty,
                        SUM(line_total) AS total_revenue,
                        SAFE_DIVIDE(SUM(qty), DATE_DIFF(yesterday, MIN(order_date_created), DAY) + 1) AS avg_daily_sales,
                        MIN(order_date_created) AS first_order_date,
                        MAX(order_date_created) AS last_order_date
                FROM `Gold.obt`
                GROUP BY item_sku
                )
                SELECT *
                FROM product_metrics
                ORDER BY total_qty DESC;
                '''
        )

    except Exception as e:
        log.error(f'Error while creating product metrics table in BigQuery: {e}')