from fastapi import APIRouter, Depends, status, UploadFile, File, Form, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.database import get_db
from app.repositories.machine_repo import MachineRepository
from app.repositories.audit_repo import AuditRepository
from app.integrations.storage.minio_client import MinioClient
from app.services.machine_service import MachineService
from app.schemas.machine.requests import MachineCreateRequest, MachineUpdateRequest
from app.schemas.machine.responses import MachineResponse
from app.schemas.common import PaginatedResponse
from app.api.dependencies import require_editor 
from app.schemas.common import ResponseOK
from app.models.user import User

router = APIRouter()

def get_machine_service(db: AsyncSession = Depends(get_db)) -> MachineService:
    return MachineService(
        machine_repo=MachineRepository(db),
        audit_repo=AuditRepository(db),
        storage_client=MinioClient()
    )

@router.get("/", response_model=PaginatedResponse[MachineResponse], summary="Получить список всей техники (Открыто для всех)")
async def get_machines(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    machine_repo = MachineRepository(db)
    machines = await machine_repo.get_all_descending(limit, offset)
    total = await machine_repo.count()
    return PaginatedResponse(total=total, limit=limit, offset=offset, data=machines)


@router.post("/", response_model=ResponseOK[MachineResponse], status_code=status.HTTP_201_CREATED, summary="Создать карточку техники (Только Админ/Редактор)")
async def create_machine(
    title: str = Form(...),
    description: str | None = Form(None),
    price: float | None = Form(None),
    specifications: str = Form("{}"), 
    files: list[UploadFile] = File(default=[]),
    machine_srv: MachineService = Depends(get_machine_service),
    current_admin: User = Depends(require_editor)
):
    specs_dict = json.loads(specifications)
    schema = MachineCreateRequest(title=title, description=description, price=price, specifications=specs_dict)
    
    valid_files = [f for f in files if not isinstance(f, str) and f.size > 0]
    
    machine = await machine_srv.create_machine(schema, valid_files, current_admin.id)
    
    return {"data": machine}


@router.put("/{machine_id}", response_model=ResponseOK[MachineResponse], summary="Обновить карточку техники (Только Админ/Редактор)")
async def update_machine(
    machine_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    price: float | None = Form(None),
    specifications: str | None = Form(None),
    files: list[UploadFile] = File(default=[]),
    machine_srv: MachineService = Depends(get_machine_service),
    current_admin: User = Depends(require_editor)
):
    specs_dict = json.loads(specifications) if specifications else None
    schema = MachineUpdateRequest(title=title, description=description, price=price, specifications=specs_dict)
    
    valid_files = [f for f in files if not isinstance(f, str) and f.size > 0]
    
    updated_machine = await machine_srv.update_machine(machine_id, schema, valid_files, current_admin.id)
    
    return {"data": updated_machine}


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить карточку техники (Только Админ/Редактор)")
async def delete_machine(
    machine_id: int,
    machine_srv: MachineService = Depends(get_machine_service),
    current_admin: User = Depends(require_editor)
):
    await machine_srv.delete_machine(machine_id, current_admin.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{machine_id}", response_model=ResponseOK[MachineResponse], summary="Получить детальную карточку техники по ID (Открыто для всех)")
async def get_machine_detail(
    machine_id: int,
    db: AsyncSession = Depends(get_db)
):
    machine_repo = MachineRepository(db)
    machine = await machine_repo.get_by_id(machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Карточка техники не найдена"
        )
    return {"data": machine}