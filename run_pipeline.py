from datetime import datetime

import utils.logger as logger
from ETL.Bronze import products, users, orders
from ETL.Silver import fct_orders, dim_products, dim_users
from ETL.Gold import obt, user_metrics, product_metrics


def extract(date: str) -> None:

    products.extract_and_save_report(date)
    users.extract_and_save_report(date)
    orders.extract_and_save_report(date)


def transform(date: str) -> None:

    dim_products.create_silver_table(date)
    dim_users.create_silver_table(date)
    fct_orders.create_silver_table(date)


def load(date: str) -> None:

    obt.create_gold_table(date)
    # user_metrics.create_gold_table(date)
    # product_metrics.create_gold_table(date)


def main() -> None:
    
    log = logger.get_logger(__name__)
    # date = datetime.now().strftime('%Y-%m-%d')
    date = '2025-03-29'

    log.info('Starting ETL - Extraction')
    extract(date)

    log.info('Starting ETL - Transformation')
    transform(date)

    log.info('Starting ETL - Load')
    load(date)

    log.info(f'Pipeline completed')

if __name__ == '__main__':
   
    main()