from datetime import datetime

from google_cloud_storage_utils import list_bucket_contents, download_from_bucket, download_from_bucket_as_bytes, upload_to_bucket, check_file_exists

from ETL.Bronze import products, users, orders
from ETL.Silver import products, users, orders

def main():

    today = datetime.now().strftime('%Y-%m-%d')
    # orders.extract_report(today)
    # products.extract_report(today)
    # users.extract_report(today)

if __name__ == '__main__':
   
    main()
