from datetime import datetime
import logger
from ETL.Bronze import products, users, orders
from ETL.Silver import fct_orders, dim_products, dim_users
from ETL.Gold import obt, user_metrics, product_metrics


def main():

    log = logger.get_logger(__name__)
    log.info('Starting ETL - Extraction')

    # date = datetime.now().strftime('%Y-%m-%d')
    date = '2025-03-07'
    products_df = products.extract_and_save_report(date)
    users_df = users.extract_and_save_report(date)
    orders_df = orders.extract_and_save_report(date)

    log.info('Starting ETL - Transformation')

    dim_products.create_silver_table(
        dim_products.validate_and_transform_report(products_df)
    )
    dim_users.create_silver_table(
        dim_users.validate_and_transform_report(users_df)
    )
    fct_orders.create_silver_table(
        fct_orders.validate_and_transform_report(orders_df)
    )

    log.info('Starting ETL - Load')

    obt.create_gold_table(date)
    user_metrics.create_gold_table()
    product_metrics.create_gold_table()

    log.info(f'Pipeline completed')

if __name__ == '__main__':
   
    main()