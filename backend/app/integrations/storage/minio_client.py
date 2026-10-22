import asyncio
import io
import logging
import uuid

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    def _convert_image_to_webp(self, byte_content: bytes) -> bytes:
        try:
            image = Image.open(io.BytesIO(byte_content))
            webp_buffer = io.BytesIO()
            image.save(webp_buffer, format="WEBP", quality=80)
            return webp_buffer.getvalue()
        except Exception as e:
            logger.error("Pillow conversion error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не является корректным изображением",
            )

    async def upload_file(self, file: UploadFile) -> str:
        unique_filename = f"{uuid.uuid4()}.webp"

        try:
            file_content = await file.read()

            webp_content = await asyncio.to_thread(
                self._convert_image_to_webp, file_content
            )

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=webp_content,
                ContentType="image/webp",
            )

            return f"/media/{unique_filename}"

        except ClientError as e:
            logger.error("MinIO Upload Error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось загрузить изображение",
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
            logger.error("MinIO Delete Error: %s", e)
