from datetime import datetime
import argparse
from src.utils import download_file, extract_files, cleanup_extraction
from src.s3_utils import MinioClient
from src.yara_scanner import process_samples
from dotenv import load_dotenv
import os
from src.logging_config import logger

load_dotenv()

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_PORT = os.getenv('S3_PORT')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')

def main():
    logger.info("vx-underground FP started")

    # Инициализируем MinioClient
    minio_client = MinioClient(endpoint=f"{S3_ENDPOINT}:{S3_PORT}", access_key=S3_ACCESS_KEY, secret_key=S3_SECRET_KEY)
    if not minio_client:
        logger.error(f"Failed to initialize MinioClient: {str(e)}")

    parser = argparse.ArgumentParser(description="Process VX Underground files")
    parser.add_argument("--year", type=int, help="Year in YYYY format")
    parser.add_argument("--month", type=int, help="Month in MM format")
    parser.add_argument("--day", type=int, help="Day in DD format")
    args = parser.parse_args()

    if not all([args.year, args.month, args.day]):
        raise ValueError("All date components must be provided:")

    target_date = datetime(args.year, args.month, args.day)

    # Скачиваем с VX-underground архив со всеми файлами за день
    zip_path = download_file(target_date.strftime("%Y"), target_date.strftime("%m"), target_date.strftime("%d"))
    if not zip_path:
        logger.error(f"Failed to download archive for {target_date.strftime('%Y.%m.%d')}")
        return

    #zipdata = os.path.join(os.getcwd(), "2024.11.01.7z") # для дебага
    
    # Распаковываем все файлы в ./tmp
    extracted_files = extract_files(zip_path)
    if not extracted_files:
        logger.error(f"Failed to extract files for {target_date.strftime('%Y.%m.%d')}")
        return

    # Сканируем файлы с помощью Yara
    process_samples( os.path.join(os.getcwd(), "tmp"), os.path.join(os.getcwd(), "rules"))
    
    try:
        S3_BUCKET_NAME = f"{target_date.strftime('%Y')}-{target_date.strftime('%m')}-{target_date.strftime('%d')}" + "-vx-underground"
        minio_client.create_bucket(S3_BUCKET_NAME)
        # Загружаем файлы в бакет
        for file in os.listdir(os.path.join(os.getcwd(), "tmp")):
            minio_client.upload_file(S3_BUCKET_NAME, os.path.join(os.getcwd(), "tmp", file))
    except Exception as e:
        logger.error(f"Failed to upload files to S3: {str(e)}")

    # Чистим данные
    #cleanup_extraction("2024.11.01.7z") # для дебага

    cleanup_extraction(zip_path)

if __name__ == "__main__":
    
    main()
