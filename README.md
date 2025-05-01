# eCommerce ETL Pipeline

## Overview

A project built to better understand the ETL process in data engineering and analysis, allowing me to gain practical experience with **Python**, **SQL**, **Google Cloud**, **Apache Airflow**, **Docker** and **Looker Studio**. The pipeline extracts data from daily CSV reports and API sources, transforming and loading it into BigQuery, where it is visualised in Looker Studio to present valuable eCommerce metrics.

[View the eCommerce Dashboard here.](https://lookerstudio.google.com/reporting/97af44b1-e064-4d94-a599-be2af56907d6/page/pWi5E)

**Sections**  
[Technologies Used](#technologies-used)  
[Architecture](#Architecture)  
[Data Source](#data-source)  
[Data Pipeline](#data-pipeline)  
[Data Visualisation](#data-visualisation)  

## Technologies Used

**Programming**: Python, SQL  
**Cloud**: Google Cloud Storage, BigQuery  
**Data Transformation**: Pandas  
**Orchestration**: Apache Airflow  
**Visualization**: Google Looker Studio  
**Containerization**: Docker  

## Architecture
![ETL Architecture](img/Architecture.png?raw=true "ETL Architecture")


## Data Source
The data used in this project is from my [Fake eCommerce Data Generator](https://github.com/srl-git/Fake_ecommerce_data) and is sourced from daily CSV reports and API calls. 

The data consists of:
- Product data: Item details including price, release date, active status
- User data: Customer details including name, address, email
- Order data: Sales details with user ID, item, quantity, order date


## Data Pipeline

#### Orchestration

Apache Airflow is used to manage and schedule the data pipeline on a daily basis, with email and telegram notifications for task or DAG failures. To keep costs low for this project, I chose to run Airflow locally using Docker rather than using Google Cloud Composer, which would have been much more expensive for this use case.

![Airflow Graph](img/Airflow.png?raw=true "Airflow Graph")

#### Extract/Transform/Load

**Extract**  
- Data is extracted from CSV reports and API calls.  
- Saved to Google Cloud Storage as a raw data landing area.

**Transform**  
- Data is validated and transformed using Python and Pandas.

**Load**  
- Cleaned data is loaded into BigQuery.  
- Modeled into fact and dimension tables.  
- Joined and aggregated into:
    - An OBT (One Big Table) partitioned by order date
    - User and product metrics tables
    - A daily sales report


#### Daily Sales Report Email
The pipeline generates a report highlighting the previous day's top 15 sellers. The report is emailed with a simple HTML table displaying product names, quantities, and revenues.

## Data Visualisation

With the data stored in BigQuery, I chose Looker Studio for data visualisation due to its native integration and interactive filtering. The dashboard features three reports, allowing users to gain insights across different dimensions. [View the eCommerce Dashboard here.](https://lookerstudio.google.com/reporting/97af44b1-e064-4d94-a599-be2af56907d6/page/pWi5E)


##### Overview
An overview of eCommerce activity with order, product and customer metrics. Includes a date range filter and comparisons to the previous period.

![Dashboard Overview](img/Dashboard_Overview.png?raw=true "Dashboard Overview")

##### Item Breakdown
A detailed breakdown of sales by product, territory and date with interactive filters for each dimension.

![Dashboard Item Breakdown](img/Dashboard_Breakdown.png?raw=true "Dashboard Item Breakdown")

##### Item Performance
Visualises sales over time, aligning products by their launch or release date. Switch between daily and weekly views to analyse and compare performance trends.

![Dashboard Item Performance](img/Dashboard_Performance.png?raw=true "Dashboard Item Performance")

## Limitations/Future improvements

There are some limitations in this project, some that I intend to improve and others are cost related:

##### Data pipeline in native Python and SQL

Instead of using Airflow’s Google Cloud operators, I coded everything manually. I mainly did this to get more practice with Python and SQL but in a real setup, using the operators would make things cleaner and more reliable.

##### Airflow is running locally

To avoid considerable costs running Cloud Composer for just this small pipeline, I am running Airflow in a Docker container on my machine. It’s not scalable or production ready but it let me build and test everything without worrying about fees.

##### Using pandas for data processing

I'm handling all the data validation and transformation in pandas. It works fine because the data extracted each day is small, it also gave me a chance to get better with pandas.

##### No checks for data readiness

I should implement Airflow sensor's like FileSensor or BigQueryTableSensor to make sure data is ready before moving to the next step in the pipeline. This is currently covered with task failures and retries but using a sensor would be much better.
