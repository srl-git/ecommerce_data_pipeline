import google_cloud_bq_utils as bq
import logger

log = logger.get_logger(__name__)


def create_gold_table(date: str):
    
    log.info('Creating/updating product metrics on BigQuery table Gold.product_metrics.')
    try:
        bq.run_bq_query(f'''
                CREATE TABLE IF NOT EXISTS Gold.product_metrics AS
                SELECT
                    item_sku,
                    SUM(qty) AS total_sold,
                    SUM(line_total) AS total_revenue,
                    MAX(order_date_created) AS last_order_date
                FROM `Gold.obt`
                GROUP BY item_sku;
            '''
        )
        bq.run_bq_query(f'''
                MERGE Gold.product_metrics AS target
                USING (
                    SELECT
                        item_sku,
                        SUM(qty) AS daily_total_sold,
                        SUM(line_total) AS daily_total_revenue,
                        MAX(order_date_created) AS daily_last_order_date
                    FROM `Gold.obt`
                    WHERE DATE(order_date_created) = '{date}'
                    GROUP BY item_sku
                ) AS source
                ON target.item_sku = source.item_sku
                WHEN MATCHED THEN
                    UPDATE SET
                        target.total_sold = target.total_sold + source.daily_total_sold,
                        target.total_revenue = target.total_revenue + source.daily_total_revenue,
                        target.last_order_date = GREATEST(target.last_order_date, source.daily_last_order_date)
                WHEN NOT MATCHED THEN
                    INSERT (item_sku, total_sold, total_revenue, last_order_date)
                    VALUES (source.item_sku, source.daily_total_sold, source.daily_total_revenue, source.daily_last_order_date);
            '''
        )
    except Exception as e:
        log.error(f'Error while creating product metrics table in BigQuery: {e}')