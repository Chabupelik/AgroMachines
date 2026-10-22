import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from app.api.dependencies import require_editor
from app.db.database import DbSession
from app.db.redis import RedisClient
from app.integrations.storage.minio_client import MinioClient
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.machine_repo import MachineRepository
from app.schemas.common import PaginatedResponse, ResponseOK
from app.schemas.machine.requests import MachineCreateRequest, MachineUpdateRequest
from app.schemas.machine.responses import MachineResponse
from app.services.machine_service import MachineService

router = APIRouter()


def get_machine_service(db: DbSession) -> MachineService:
    return MachineService(
        machine_repo=MachineRepository(db),
        audit_repo=AuditRepository(db),
        storage_client=MinioClient(),
    )


@router.get("/", response_model=PaginatedResponse[MachineResponse])
async def get_machines(
    db: DbSession,
    redis: RedisClient,
    limit: int = 10,
    offset: int = 0,
):
    cache_key = f"machines:list:{limit}:{offset}"
    cached_data = await redis.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    machine_repo = MachineRepository(db)
    machines_db = await machine_repo.get_all_descending(limit, offset)
    total = await machine_repo.count()

    machine_schemas = [MachineResponse.model_validate(m) for m in machines_db]
    response_data = PaginatedResponse(
        total=total, limit=limit, offset=offset, data=machine_schemas
    )

    await redis.setex(cache_key, 3600, response_data.model_dump_json())

    return response_data


@router.post(
    "/",
    response_model=ResponseOK[MachineResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Создать технику (только ред./адм.)",
)
async def create_machine(
    title: str = Form(...),
    description: str | None = Form(None),
    price: float | None = Form(None),
    specifications: str = Form("{}"),
    files: list[UploadFile] = File(default=[]),
    machine_srv: Annotated[MachineService, Depends(get_machine_service)] = None,
    current_admin: Annotated[User, Depends(require_editor)] = None,
):
    specs_dict = json.loads(specifications)
    schema = MachineCreateRequest(
        title=title, description=description, price=price, specifications=specs_dict
    )
    valid_files = [f for f in files if not isinstance(f, str) and f.size > 0]
    machine = await machine_srv.create_machine(schema, valid_files, current_admin.id)
    return {"data": machine}


@router.put("/{machine_id}")
async def update_machine(
    machine_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    price: int | None = Form(None),
    specifications: str | None = Form(None),
    is_available: bool | None = Form(None),
    existing_image_urls: str | None = Form(None),
    files: list[UploadFile] = File(default=[]),
    current_admin: Annotated[User, Depends(require_editor)] = None,
    machine_srv: Annotated[MachineService, Depends(get_machine_service)] = None,
):
    specs = json.loads(specifications) if specifications else None
    urls = json.loads(existing_image_urls) if existing_image_urls else None
    schema = MachineUpdateRequest(
        title=title,
        description=description,
        price=price,
        specifications=specs,
        existing_image_urls=urls,
        is_available=is_available,
    )
    updated_machine = await machine_srv.update_machine(
        machine_id, schema, files, current_admin.id
    )
    return {"status": "ok", "data": updated_machine}


@router.delete(
    "/{machine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить технику (только ред./адм.)",
)
async def delete_machine(
    machine_id: int,
    machine_srv: Annotated[MachineService, Depends(get_machine_service)] = None,
    current_admin: Annotated[User, Depends(require_editor)] = None,
):
    await machine_srv.delete_machine(machine_id, current_admin.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{machine_id}", response_model=ResponseOK[MachineResponse])
async def get_machine_detail(
    machine_id: int,
    db: DbSession,
    redis: RedisClient,
):
    cache_key = f"machine:detail:{machine_id}"
    cached_machine = await redis.get(cache_key)

    if cached_machine:
        return {"status": "ok", "data": json.loads(cached_machine)}

    machine_repo = MachineRepository(db)
    machine = await machine_repo.get_by_id(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Такая машина не найдена")

    schema_data = MachineResponse.model_validate(machine)
    await redis.setex(cache_key, 3600, schema_data.model_dump_json())

    return {"status": "ok", "data": machine}
