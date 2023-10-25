from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_before_delete,
                                check_charity_project_before_edit,
                                check_charity_project_name_duplicate,
                                check_full_amount_value)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investing import investation


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        obj_in: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Создает благотворительный проект.
        Только для суперюзеров.
    """
    await check_charity_project_name_duplicate(obj_in.name, session)
    new_charity_project = await charity_project_crud.create(obj_in, session)
    new_charity_project = await investation(
        new_charity_project, Donation, session
    )
    return new_charity_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,

    description='Получает список всех проектов.',
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session)
):
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        charity_project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Закрытый проект нельзя редактировать.
        Только для суперюзеров.
    """
    charity_project = await check_charity_project_before_edit(
        charity_project_id, session
    )
    if obj_in.name is not None:
        await check_charity_project_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        await check_full_amount_value(
            obj_in.full_amount, charity_project.invested_amount
        )
    updated_charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    updated_charity_project = await investation(
        updated_charity_project, Donation, session
    )
    return updated_charity_project


@router.delete(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        charity_project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Удаляет проект. Нельзя удалить активный проект,
        его можно только закрыть.
        Только для суперюзеров.
    """
    charity_project = await check_charity_project_before_delete(
        charity_project_id, session
    )
    return await charity_project_crud.remove(charity_project, session)
