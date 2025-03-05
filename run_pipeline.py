from datetime import datetime
import pandas as pd
from ETL.Bronze import products, users, orders
from ETL.Silver import fct_orders, dim_products, dim_users
from ETL.Gold import obt


def main():

    # date = datetime.now().strftime('%Y-%m-%d')
    date = '2025-03-04'
    products_df = products.extract_and_save_report(date)
    users_df = users.extract_and_save_report(date)
    orders_df = orders.extract_and_save_report(date)

    dim_products_df = dim_products.validate_and_transform_report(products_df)
    dim_users_df = dim_users.validate_and_transform_report(users_df)
    fct_orders_df = fct_orders.validate_and_transform_report(orders_df)

    obt_df = obt.join_reports(date)

if __name__ == '__main__':
   
    main()