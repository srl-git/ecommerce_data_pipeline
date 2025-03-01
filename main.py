from datetime import datetime
import pandas as pd
from ETL.Bronze import products, users, orders
from ETL.Silver import fct_orders, dim_products, dim_users

fct_orders_config = {

    'expected_cols': ['order_line_id', 'order_id', 
                      'user_id', 'item_sku', 'qty', 
                      'item_price', 'date_created'],
    
    'id_cols': ['order_line_id'],
    'date_cols': ['date_created']
}

def main():

    # df = pd.read_csv('Order_report_2025-02-19.csv')
    # today = datetime.now().strftime('%Y-%m-%d')
    today = '2025-02-20'
    # products.extract_report(today)
    # users.extract_report(today)
    # orders.extract_report(today)
    # dim_products_df = dim_products.load_report(today)
    fct_orders.transform_report(today, **fct_orders_config)

if __name__ == '__main__':
   
    main()