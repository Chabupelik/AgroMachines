import asyncio
import logging
import uuid

import redis.asyncio as aioredis
from fastapi import HTTPException, UploadFile, status
from redis.exceptions import LockError

from app.integrations.storage.minio_client import MinioClient
from app.models.machine import Machine
from app.repositories.audit_repo import AuditRepository
from app.repositories.machine_repo import MachineRepository
from app.schemas.common import PaginatedResponse
from app.schemas.machine.requests import MachineCreateRequest, MachineUpdateRequest
from app.schemas.machine.responses import MachineResponse

logger = logging.getLogger(__name__)


class MachineService:
    def __init__(
        self,
        machine_repo: MachineRepository,
        audit_repo: AuditRepository,
        storage_client: MinioClient,
        redis: aioredis.Redis | None = None,
    ):
        self.machine_repo = machine_repo
        self.audit_repo = audit_repo
        self.storage_client = storage_client
        self.redis = redis

    async def _invalidate_cache(self, machine_id: int | None = None) -> None:
        if not self.redis:
            return
        try:
            keys_to_delete: list[str] = []
            if machine_id is not None:
                keys_to_delete.append(f"machine:detail:{machine_id}")

            async for key in self.redis.scan_iter("machines:list:*"):
                keys_to_delete.append(key)

            if keys_to_delete:
                await self.redis.delete(*keys_to_delete)
        except Exception as e:
            logger.warning("Не удалось инвалидировать кэш машин: %s", e)

    async def get_machines(
        self, limit: int = 10, offset: int = 0
    ) -> PaginatedResponse[MachineResponse]:
        cache_key = f"machines:list:{limit}:{offset}"
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    return PaginatedResponse[MachineResponse].model_validate_json(
                        cached
                    )

                lock_key = f"lock:{cache_key}"
                try:
                    async with self.redis.lock(
                        lock_key, timeout=2.0, blocking_timeout=0.25
                    ):
                        cached = await self.redis.get(cache_key)
                        if cached:
                            return PaginatedResponse[
                                MachineResponse
                            ].model_validate_json(cached)

                        machines_db = await self.machine_repo.get_all_descending(
                            limit, offset
                        )
                        total = await self.machine_repo.count()
                        machine_schemas = [
                            MachineResponse.model_validate(m) for m in machines_db
                        ]
                        result = PaginatedResponse(
                            total=total,
                            limit=limit,
                            offset=offset,
                            data=machine_schemas,
                        )
                        await self.redis.setex(
                            cache_key, 3600, result.model_dump_json()
                        )
                        return result
                except LockError:
                    pass
            except Exception as e:
                logger.warning("Ошибка при работе с кэшем списка машин: %s", e)

        machines_db = await self.machine_repo.get_all_descending(limit, offset)
        total = await self.machine_repo.count()
        machine_schemas = [MachineResponse.model_validate(m) for m in machines_db]
        return PaginatedResponse(
            total=total, limit=limit, offset=offset, data=machine_schemas
        )

    async def get_machine_detail(self, machine_id: int) -> MachineResponse:
        cache_key = f"machine:detail:{machine_id}"
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    return MachineResponse.model_validate_json(cached)

                lock_key = f"lock:{cache_key}"
                try:
                    async with self.redis.lock(
                        lock_key, timeout=2.0, blocking_timeout=0.25
                    ):
                        cached = await self.redis.get(cache_key)
                        if cached:
                            return MachineResponse.model_validate_json(cached)

                        machine = await self.machine_repo.get_by_id(machine_id)
                        if not machine:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail="Такая машина не найдена",
                            )

                        schema_data = MachineResponse.model_validate(machine)
                        await self.redis.setex(
                            cache_key, 3600, schema_data.model_dump_json()
                        )
                        return schema_data
                except LockError:
                    pass
            except HTTPException:
                raise
            except Exception as e:
                logger.warning("Ошибка при работе с кэшем деталей машины: %s", e)

        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Такая машина не найдена",
            )
        return MachineResponse.model_validate(machine)

    async def create_machine(
        self,
        schema: MachineCreateRequest,
        files: list[UploadFile] | None,
        user_id: uuid.UUID,
    ) -> Machine:
        image_urls = []
        if files:
            upload_tasks = [self.storage_client.upload_file(file) for file in files]
            image_urls = await asyncio.gather(*upload_tasks)

        new_machine = Machine(
            title=schema.title,
            description=schema.description,
            specifications=schema.specifications,
            price=schema.price,
            is_available=schema.is_available,
            image_urls=image_urls,
        )
        saved_machine = await self.machine_repo.add(new_machine)

        await self.audit_repo.log_action(
            action="CREATE_MACHINE",
            entity_type="machine",
            entity_id=saved_machine.id,
            user_id=user_id,
        )
        await self.machine_repo.session.commit()
        await self._invalidate_cache(machine_id=saved_machine.id)
        return saved_machine

    async def update_machine(
        self,
        machine_id: int,
        schema: MachineUpdateRequest,
        files: list[UploadFile] | None,
        user_id: uuid.UUID,
    ) -> Machine:
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Карточка техники не найдена",
            )

        existing_urls = (
            schema.existing_image_urls
            if schema.existing_image_urls is not None
            else machine.image_urls
        )

        urls_to_delete = set(machine.image_urls) - set(existing_urls)
        if urls_to_delete:
            delete_tasks = [
                self.storage_client.delete_file(old_url) for old_url in urls_to_delete
            ]
            await asyncio.gather(*delete_tasks, return_exceptions=True)

        new_image_urls = []
        if files:
            upload_tasks = [self.storage_client.upload_file(file) for file in files]
            new_image_urls = await asyncio.gather(*upload_tasks)

        machine.image_urls = list(existing_urls) + new_image_urls

        if schema.title is not None:
            machine.title = schema.title
        if schema.description is not None:
            machine.description = schema.description
        if schema.specifications is not None:
            machine.specifications = schema.specifications
        if schema.price is not None:
            machine.price = schema.price
        if schema.is_available is not None:
            machine.is_available = schema.is_available

        await self.audit_repo.log_action(
            action="UPDATE_MACHINE",
            entity_type="machine",
            entity_id=machine.id,
            user_id=user_id,
        )

        await self.machine_repo.session.commit()
        await self.machine_repo.session.refresh(machine)
        await self._invalidate_cache(machine_id=machine.id)
        return machine

    async def delete_machine(self, machine_id: int, user_id: uuid.UUID):
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Карточка техники не найдена",
            )

        if machine.image_urls:
            delete_tasks = [
                self.storage_client.delete_file(url) for url in machine.image_urls
            ]
            await asyncio.gather(*delete_tasks, return_exceptions=True)

        await self.machine_repo.delete(machine)

        await self.audit_repo.log_action(
            action="DELETE_MACHINE",
            entity_type="machine",
            entity_id=machine_id,
            user_id=user_id,
        )
        await self.machine_repo.session.commit()
        await self._invalidate_cache(machine_id=machine_id)
