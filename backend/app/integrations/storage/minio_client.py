import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
import uuid
from app.core.config import settings

class MinioClient:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    async def upload_file(self, file: UploadFile) -> str:
        extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        try:
            file_content = await file.read()
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=file.content_type
            )
            
            return f"/media/{unique_filename}"
            
        except ClientError as e:
            print(f"❌ MinIO Upload Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось загрузить изображение в облачное хранилище"
            )
        finally:
            await file.close()

    def delete_file(self, file_url: str):
        if not file_url:
            return
        filename = file_url.split("/")[-1]
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=filename)
        except ClientError as e:
            print(f"❌ MinIO Delete Error: {e}")