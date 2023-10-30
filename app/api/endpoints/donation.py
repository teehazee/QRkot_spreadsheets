from typing import List

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import (
    current_superuser,
    current_user
)
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.services.investing import investation
from app.schemas.donation import (
    DonationCreate,
    DonationDB,
    DonationView
)

router = APIRouter()


@router.post(
    '/',
    response_model=DonationView,
    dependencies=[Depends(current_user)],
    response_model_exclude_none=True
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    new_donation = await donation_crud.create(
        donation,
        session,
        user,
        do_commit=False
    )
    session.add_all(
        [*investation(
            new_donation,
            await charity_project_crud.get_not_invested(session)
        ), new_donation
        ]
    )
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=List[DonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех пожертвований.
        Только для суперюзеров.
    """
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=List[DonationView],
    response_model_exclude_none=True
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """Получить список моих пожертвований."""
    return await donation_crud.get_user_donations(
        session=session, user=user
    )
