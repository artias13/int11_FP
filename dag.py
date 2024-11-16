from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from src.s3_utils import MinioClient
from src.yara_scanner import process_samples
from src.utils import download_file, extract_files, cleanup_extraction
from src.logging_config import logger

load_dotenv()

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_PORT = os.getenv('S3_PORT')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')

def process_vx_underground(**kwargs):
    # Initialize MinioClient
    minio_client = MinioClient(endpoint=f"{S3_ENDPOINT}:{S3_PORT}", access_key=S3_ACCESS_KEY, secret_key=S3_SECRET_KEY)
    
    # Download archive
    zip_path = download_file(datetime.now().strftime("%Y"), datetime.now().strftime("%m"), datetime.now().strftime("%d"))
    if not zip_path:
        logger.error(f"Failed to download archive for {datetime.now().strftime('%Y.%m.%d')}")
        return
    
    # Extract files
    extracted_files = extract_files(zip_path)
    if not extracted_files:
        logger.error(f"Failed to extract files for {datetime.now().strftime('%Y.%m.%d')}")
        return
    
    # Process samples
    process_samples(os.path.join(os.getcwd(), "tmp"), os.path.join(os.getcwd(), "rules"))
    
    try:
        target_date = datetime.now()
        S3_BUCKET_NAME = f"{target_date.strftime('%Y')}-{target_date.strftime('%m')}-{target_date.strftime('%d')}" + "-vx-underground"
        minio_client.create_bucket(S3_BUCKET_NAME)
        
        # Upload files
        for file in os.listdir(os.path.join(os.getcwd(), "tmp")):
            minio_client.upload_file(S3_BUCKET_NAME, os.path.join(os.getcwd(), "tmp", file))
    except Exception as e:
        logger.error(f"Failed to upload files to S3: {str(e)}")
    
    # Cleanup
    cleanup_extraction(zip_path)

dag = DAG(
    'vx_underground_processor',
    description='Process VX Underground files daily',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',  # Run once per day
    catchup=False,
)

process_task = PythonOperator(
    task_id='process_vx_underground',
    python_callable=process_vx_underground,
    dag=dag,
)
