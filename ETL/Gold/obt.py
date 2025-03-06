import google_cloud_bq_utils as bq
import logger

log = logger.get_logger(__name__)


def create_gold_table(date: str):
    
    log.info('Joining reports on bigquery table Gold.obt.')
    return bq.run_bq_query(f'''
                INSERT INTO `Gold.obt`
                SELECT
                    fct_orders.*,
                    dim_users.user_name,
                    dim_users.user_address,
                    dim_users.user_country,
                    dim_users.user_email,
                    dim_users.user_date_created,
                    dim_products.item_price,
                    dim_products.item_release_date,
                    dim_products.item_creation_date,
                    dim_products.item_updated_date,
                    dim_products.item_active,
                FROM
                    `Silver.fct_orders` AS fct_orders
                LEFT JOIN
                    `Silver.dim_users` AS dim_users
                    ON fct_orders.user_id = dim_users.user_id
                LEFT JOIN
                    `Silver.dim_products` AS dim_products
                    ON fct_orders.item_sku = dim_products.item_sku
                WHERE fct_orders.order_date_created = '{date}';
            '''
        )
