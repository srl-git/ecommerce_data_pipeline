import utils.google_cloud_bq_utils as bq
import utils.logger as logger

log = logger.get_logger(__name__)

def create_gold_table() -> None:

    log.info('Updating daily sales report on BigQuery table Gold.daily_sales_report.')

    try:
        bq.run_bq_query(f'''
                CREATE OR REPLACE TABLE 
                    `Gold.daily_sales_report` AS
                        SELECT
                            DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) AS sales_date,
                            item_sku,
                            SUM(qty) AS total_qty,
                            SUM(line_total) AS total_sales
                        FROM `Gold.obt`
                        WHERE DATE(order_date_created) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
                        GROUP BY item_sku
                        ORDER BY total_qty DESC
                        LIMIT 15;
                    '''
        )
    except Exception as e:
        log.error(f'Error while creating daily_sales_report table in BigQuery: {e}')
        raise