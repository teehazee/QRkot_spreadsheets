from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_project_exist,
    check_project_closed,
    check_project_amount_less_than_invested,
    check_project_name,
    check_project_is_invested,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud

from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate
)

from app.services.investing import investation


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    await check_project_name(
        charity_project.name, session
    )
    new_project = await charity_project_crud.create(
        charity_project,
        session,
        commit_choke=False
    )
    session.add_all(
        [*investation(
            new_project,
            await donation_crud.get_not_invested(session)
        ), new_project
        ]
    )
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        project_id: int,
        project_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    project_by_id = await charity_project_crud.get(project_id, session)
    check_project_exist(project_by_id)
    check_project_closed(project_by_id)
    check_project_amount_less_than_invested(
        project_in.full_amount, project_by_id.invested_amount
    )
    await check_project_name(project_in.name, session)
    return await charity_project_crud.update(
        project_by_id, project_in, session
    )


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    charity_project = await charity_project_crud.get(project_id, session)
    check_project_is_invested(charity_project)
    return await charity_project_crud.remove(charity_project, session)
