import utils.google_cloud_bq_utils as bq
import utils.logger as logger

log = logger.get_logger(__name__)


def create_gold_table(date: str):
    
    log.info('Creating/updating user metrics on BigQuery table Gold.user_metrics.')
    try:
        bq.run_bq_query(f'''
                CREATE TABLE IF NOT EXISTS Gold.user_metrics AS
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
                    user_country;
            '''
        )
        bq.run_bq_query(f'''
                MERGE Gold.user_metrics AS target
                USING ( 
                    SELECT
                        user_id,
                        user_name,
                        user_country,
                        SUM(line_total) / COUNT(DISTINCT order_id) AS avg_spend,
                        COUNT(DISTINCT(order_id)) AS total_orders,
                        SUM(line_total) AS total_spend,
                        MAX(order_date_created) AS last_order_date
                    FROM `Gold.obt`
                    WHERE DATE(order_date_created) = '{date}'
                    GROUP BY 
                        user_id,
                        user_name,
                        user_country
                ) AS source
                ON target.user_id = source.user_id
                WHEN MATCHED THEN
                    UPDATE SET
                        target.user_name = source.user_name,
                        target.user_country = source.user_country,
                        target.avg_spend = (target.total_spend + source.total_spend) / (target.total_orders + source.total_orders),
                        target.total_orders = target.total_orders + source.total_orders,
                        target.total_spend = target.total_spend + source.total_spend,
                        target.last_order_date = GREATEST(target.last_order_date, source.last_order_date)
                WHEN NOT MATCHED THEN
                    INSERT (user_id, user_name, user_country, avg_spend, total_orders, total_spend, last_order_date)
                    VALUES (source.user_id, source.user_name, source.user_country, source.avg_spend, source.total_orders, source.total_spend, source.last_order_date);
            '''
        )
    except Exception as e:
        log.error(f'Error while creating user metrics table in BigQuery: {e}')
