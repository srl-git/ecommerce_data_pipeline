import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dotenv import load_dotenv

import utils.google_cloud_bq_utils as bq
import utils.logger as logger


load_dotenv()

log = logger.get_logger(__name__)

def create_gold_table() -> None:
    """
    Create or replace the `Gold.daily_sales_report` table in BigQuery.

    Runs a query to aggregate sales data from the previous day.

    Raises:
        Exception: If the BigQuery query execution fails.
    """
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


def get_daily_sales_report() -> pd.DataFrame:
    """
    Fetch and format the `Gold.daily_sales_report` table from BigQuery.

    Formats sales values with currency symbol and renames columns for reporting.

    Raises:
        ValueError: If DataFrame is None or empty.

    Returns:
        pd.DataFrame: The formatted daily sales report.
    """
    df = bq.download_df_from_bq(
        query_or_table='Gold.daily_sales_report'
        )
    if df is None or df.empty:
        raise ValueError('No results for Gold.daily_sales_report.')
    
    df['total_sales'] = df['total_sales'].map(lambda x: f'£{x:.2f}')
    df.rename(
        inplace=True,
        columns={
            'item_sku': 'Item',
            'total_qty': 'Quantity',
            'total_sales': 'Revenue'
        }
    )
    return df


def email_daily_sales_report(to_emails: list[str], df: pd.DataFrame) -> None:
    """
    Email the Daily Sales Report table to the 'to_email' addresses.

    Args:
        to_emails (list[str]): list of recipient emails.
        df (pd.DataFrame): DataFrame containing the sales report.

    Raises:
        Exception: If sending the email fails.
    """
    html_table = df.to_html(
        columns=['Item', 'Quantity', 'Revenue'],
        buf=None,
        index=False,
        justify='left',
        escape=True
    )
    report_date = df['sales_date'][0]
    from_email = os.getenv('EMAIL','')
    body = f'<b>Top 15 sellers from {report_date}</b>'
    full_body = f'{body}<br><br>{html_table}'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ','.join(to_emails)
    msg['Subject'] = f'Daily eCommerce Sales Report: {report_date}'
    msg.attach(MIMEText(full_body, 'html'))

    smtp_server = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    password = os.getenv('SMTP_PASSWORD')

    try:
        with smtplib.SMTP(smtp_server) as server:
            server.connect(host=smtp_server, port=smtp_port)
            # server.ehlo()
            server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_emails, text)
    except Exception as e:
        log.error(f'SMTP Errror: {e}')
        raise


def send_daily_sales_report(to_emails: list[str]) -> None:
    """
    Fetch the daily_sales_report table from BigQuery, format the data and send in an email to the 'to_emails' addresses.

    Args:
        to_emails (lisr[str]): List of recipient emails.

    Raises:
        Exception: If fetching the report or sending the email fails.
    """
    log.info('Sending daily sales report email.')

    try:
        report = get_daily_sales_report()
        email_daily_sales_report(to_emails, report)

    except Exception as e:
        log.error(f'Error sending Daily Sales Report: {e}')
        raise