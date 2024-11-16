import os
from minio import Minio
from minio.error import S3Error

class MinioClient:
    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # Для локального тестирования
        )

    def create_bucket(self, bucket_name):
        # создание s3
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
            print("Created bucket", bucket_name)
        else:
            print("Bucket", bucket_name, "already exists")
    
    def upload_file(self, bucket_name, file_path):
        try:
            self.client.fput_object(
                bucket_name=bucket_name,
                object_name=file_path,
                file_path=file_path,
            )
            print(f"Файл {file_path} успешно загружен в S3")
        except S3Error as e:
            print(f"Ошибка при загрузке файла {file_path}: {e}")

    def download_file(self, bucket_name, file_path, local_path):
        try:
            self.client.fget_object(
                bucket_name=bucket_name,
                object_name=file_path,
                file_path=local_path
            )
            print(f"Файл {file_path} успешно загружен из S3")
        except S3Error as e:
            print(f"Ошибка при загрузке файла {file_path}: {e}")