import os
from minio import Minio
from minio.error import S3Error
from src.logging_config import logger
from typing import NoReturn
from pathlib import Path

class MinioClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # Для локального тестирования
        )

    def create_bucket(self, bucket_name: str) -> NoReturn:
        # создание s3
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} created")
        else:
            logger.info(f"Bucket {bucket_name} already exists")
    
    def upload_file(self, bucket_name: str, file_path: Path) -> NoReturn:
        try:
            self.client.fput_object(
                bucket_name=bucket_name,
                object_name=file_path,
                file_path=file_path,
            )
            logger.info(f"Файл {file_path} успешно загружен в S3")
        except S3Error as e:
            logger.error(f"Ошибка при загрузке файла {file_path}: {e}")

    def download_file(self, bucket_name: str, file_path: Path, local_path: Path):
        try:
            self.client.fget_object(
                bucket_name=bucket_name,
                object_name=file_path,
                file_path=local_path
            )
            print(f"Файл {file_path} успешно загружен из S3")
        except S3Error as e:
            print(f"Ошибка при загрузке файла {file_path}: {e}")