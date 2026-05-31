from fastapi import UploadFile, HTTPException, status
from app.repositories.machine_repo import MachineRepository
from app.repositories.audit_repo import AuditRepository
from app.integrations.storage.minio_client import MinioClient
from app.models.machine import Machine
from app.schemas.machine.requests import MachineCreateRequest, MachineUpdateRequest
import uuid

class MachineService:
    def __init__(self, machine_repo: MachineRepository, audit_repo: AuditRepository, storage_client: MinioClient):
        self.machine_repo = machine_repo
        self.audit_repo = audit_repo
        self.storage_client = storage_client

    async def create_machine(self, schema: MachineCreateRequest, file: UploadFile | None, user_id: uuid.UUID) -> Machine:
        """Создание новой карточки техники с загрузкой фото в MinIO"""
        image_url = None
        if file:
            image_url = await self.storage_client.upload_file(file)

        new_machine = Machine(
            title=schema.title,
            description=schema.description,
            specifications=schema.specifications,
            price=schema.price,
            image_url=image_url
        )
        saved_machine = await self.machine_repo.add(new_machine)

        await self.audit_repo.log_action(
            action="CREATE_MACHINE",
            entity_type="machine",
            entity_id=saved_machine.id,
            user_id=user_id
        )
        return saved_machine

    async def update_machine(self, machine_id: int, schema: MachineUpdateRequest, file: UploadFile | None, user_id: uuid.UUID) -> Machine:
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Карточка техники не найдена")

        if file:
            if machine.image_url:
                self.storage_client.delete_file(machine.image_url)
            machine.image_url = await self.storage_client.upload_file(file)

        if schema.title is not None: machine.title = schema.title
        if schema.description is not None: machine.description = schema.description
        if schema.specifications is not None: machine.specifications = schema.specifications
        if schema.price is not None: machine.price = schema.price

        await self.machine_repo.session.commit()
        await self.machine_repo.session.refresh(machine)

        await self.audit_repo.log_action(
            action="UPDATE_MACHINE",
            entity_type="machine",
            entity_id=machine.id,
            user_id=user_id
        )
        return machine

    async def delete_machine(self, machine_id: int, user_id: uuid.UUID):
        machine = await self.machine_repo.get_by_id(machine_id)
        if not machine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Карточка техники не найдена")

        if machine.image_url:
            self.storage_client.delete_file(machine.image_url)

        await self.machine_repo.delete(machine)

        await self.audit_repo.log_action(
            action="DELETE_MACHINE",
            entity_type="machine",
            entity_id=machine_id,
            user_id=user_id
        )