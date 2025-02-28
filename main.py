from datetime import datetime
import pandas as pd
from ETL.Bronze import products, users, orders
from ETL.Silver import fct_orders, dim_products, dim_users

def main():

    # today = datetime.now().strftime('%Y-%m-%d')
    today = '2025-02-20'
    # orders.extract_report(today)
    # products.extract_report(today)
    # users.extract_report(today)
    # dim_products_df = dim_products.load_report(today)

    fct_orders_df = fct_orders.load_report(today)
    

if __name__ == '__main__':
   
    main()
