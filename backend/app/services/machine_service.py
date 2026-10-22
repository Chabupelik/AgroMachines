import asyncio
import uuid

from fastapi import HTTPException, UploadFile, status

from app.integrations.storage.minio_client import MinioClient
from app.models.machine import Machine
from app.repositories.audit_repo import AuditRepository
from app.repositories.machine_repo import MachineRepository
from app.schemas.machine.requests import MachineCreateRequest, MachineUpdateRequest


class MachineService:
    def __init__(
        self,
        machine_repo: MachineRepository,
        audit_repo: AuditRepository,
        storage_client: MinioClient,
    ):
        self.machine_repo = machine_repo
        self.audit_repo = audit_repo
        self.storage_client = storage_client

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
        for old_url in urls_to_delete:
            try:
                self.storage_client.delete_file(old_url)
            except Exception as e:
                print(f"⚠️ Ошибка удаления старого файла {old_url} из MinIO: {e}")

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

        await self.machine_repo.session.commit()
        await self.machine_repo.session.refresh(machine)

        await self.audit_repo.log_action(
            action="UPDATE_MACHINE",
            entity_type="machine",
            entity_id=machine.id,
            user_id=user_id,
        )
        return machine

    async def delete_machine(self, machine_id: int, user_id: uuid.UUID):
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Карточка техники не найдена",
            )

        for url in machine.image_urls:
            self.storage_client.delete_file(url)

        await self.machine_repo.delete(machine)

        await self.audit_repo.log_action(
            action="DELETE_MACHINE",
            entity_type="machine",
            entity_id=machine_id,
            user_id=user_id,
        )
