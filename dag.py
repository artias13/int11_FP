from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'vx_underground_processor',
    default_args=default_args,
    description='Process VX Underground files daily',
    schedule_interval=timedelta(days=1),
)

def process_vx_underground(**kwargs):
    from src.utils import download_file, extract_files, scan_with_yara, upload_to_s3, save_scan_results
    
    today = kwargs['execution_date'].strftime("%Y.%m")
    zip_data = download_file(today)
    files = extract_files(zip_data)

    for file_content in files:
        scan_result = scan_with_yara(file_content)
        file_name = f"{kwargs['execution_date'].isoformat()}_{hash(file_content)}"
        
        upload_to_s3(f"{file_name}.bin", file_content)
        save_scan_results(scan_result, file_name)

process_task = PythonOperator(
    task_id='process_vx_underground',
    python_callable=process_vx_underground,
    dag=dag,
)

