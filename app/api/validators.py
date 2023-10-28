from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_project_name(
    charity_project_name: str,
    session: AsyncSession
) -> None:
    project = await charity_project_crud.get_charity_project_name(
        charity_project_name, session
    )
    if project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


def check_project_exist(charity_project: CharityProject) -> None:
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )


def check_project_amount_less_than_invested(
    new_full_amount: int,
    invested_amount: int
) -> None:
    if (
        new_full_amount is not None and
        new_full_amount < invested_amount
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Сумма не может быть меньше внесённой!',
        )


def check_project_is_invested(charity_project: CharityProject) -> None:
    if charity_project.invested_amount != 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


def check_project_closed(charity_project: CharityProject) -> None:
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
