from http import HTTPStatus as St

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_charity_project_name_duplicate(
        charity_project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_charity_project_id_by_name(
        charity_project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=St.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exist(
        charity_project_id: int,
        session: AsyncSession
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        charity_project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=St.NOT_FOUND,
            detail='Проект не найден!'
        )
    return charity_project


async def check_charity_project_before_edit(
        charity_project_id: int,
        session: AsyncSession
) -> CharityProject:
    charity_project = await check_charity_project_exist(
        charity_project_id, session
    )
    if charity_project.fully_invested is True:
        raise HTTPException(
            status_code=St.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charity_project


async def check_charity_project_before_delete(
        charity_project_id: int,
        session: AsyncSession
) -> CharityProject:
    charity_project = await check_charity_project_exist(
        charity_project_id, session
    )
    if charity_project.fully_invested is True:
        raise HTTPException(
            status_code=St.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    if charity_project.invested_amount != 0:
        raise HTTPException(
            status_code=St.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return charity_project


async def check_full_amount_value(
        full_amount: int,
        invested_amount: int
) -> None:
    if full_amount < invested_amount:
        raise HTTPException(
            status_code=St.BAD_REQUEST,
            detail='Требуемая сумма не может быть меньше уже внесённой суммы!'
        )
