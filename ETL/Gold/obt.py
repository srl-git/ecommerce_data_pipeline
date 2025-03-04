import pandas as pd
import google_cloud_bq_utils as bq

def join_reports(date: str):

    return bq.run_bq_query(f'''
                INSERT INTO `ecommerce.obt`
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
                    `ecommerce.fct_orders` AS fct_orders
                LEFT JOIN
                    `ecommerce.dim_users` AS dim_users
                    ON fct_orders.user_id = dim_users.user_id
                LEFT JOIN
                    `ecommerce.dim_products` AS dim_products
                    ON fct_orders.item_sku = dim_products.item_sku
                WHERE fct_orders.order_date_created = '{date}';
            '''
        )

    # orders_and_users_df = pd.merge(fct_orders_df, dim_users_df, on='user_id', how='left')

    # use SQL to select and join tables from silver layer tables
