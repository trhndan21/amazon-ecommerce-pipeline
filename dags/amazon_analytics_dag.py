from airflow import DAG
from datetime import datetime
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator as PythonOperation
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.bash import BashOperator

# --- PYTHON func: Load Parquet from MinIO to Postgres ---
def load_parquet_to_postgres():
    # 1. Connect S3/MinIO to read Parquet file
    # Use pandas to read directly from S3 (need to configure storage_options)
    storage_options = {
        "key": "minio",
        "secret": "minio123",
        "client_kwargs": {"endpoint_url": "http://minio:9000"}
    }
    df = pd.read_parquet("s3://amazon-bucket/clean/amazon_sales", storage_options=storage_options)

    # 2. Connect Postgres and write data
    pg_hook= PostgresHook(postgres_conn_id='postgres_default')
    engine= pg_hook.get_sqlalchemy_engine()
    df.to_sql('amazon_sales', con=engine, schema='amazon', if_exists='replace', index=False)

# --- DEFINE DAG ---
with DAG(
    'amazon_analytics_dag',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2025, 1, 1),
        'retries': 0,
    },
    schedule_interval='@daily',
    catchup=False,
) as dag:
    # TASK 1: Create Bucket in MinIO
    create_s3_bucket = S3CreateBucketOperator(
        task_id= "create_S3_bucket", bucket_name="amazon-bucket", aws_conn_id="minio_default"
    )

    # TASK 2: Upload CSV from Local to MinIO
    upload_to_S3= LocalFilesystemToS3Operator(
        task_id= "upload_to_S3",
        filename= "/opt/airflow/data/amazon_sales.csv" ,
        dest_key="raw/amazon_sales.csv",
        dest_bucket="amazon-bucket",
        aws_conn_id="minio_default",
        replace= True
    )

    # TASK 3: Run Spark job to process data
    process_data= SparkSubmitOperator(
        task_id= "process_data",
        application='/opt/airflow/dags/scripts/spark/process_reviews_sales.py',
        conn_id='spark_default', #id to connect to Spark cluster
        application_args=[
            "--input", f"s3a://amazon-bucket/raw/amazon_sales.csv",
            "--output", f"s3a://amazon-bucket/clean/amazon_sales"
        ],
        # Configure Spark to run inside Docker
        conf={"spark.master": "local[*]", 
              "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.11.1026"}
    )

    # TASK 4: Load clean data from MinIO to Postgres
    load_to_postgres= PythonOperation(
        task_id= "load_to_postgres",
        python_callable=load_parquet_to_postgres
    )

    # TASK 5: Genarate dashboard
    generate_dashboard= BashOperator(
        task_id= "generate_dashboard",
        bash_command='quarto render /opt/airflow/dags/scripts/dashboard/dashboard.qmd'
    )

    # --- COORDINATE FLOW ---
    create_s3_bucket >> upload_to_S3 >> process_data >> load_to_postgres >> generate_dashboard





