from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDReservation(CRUDBase):

    async def get_user_donations(
        self, session: AsyncSession, user: User
    ) -> Optional[Donation]:
        return (
            await session.execute(
                select(Donation).where(
                    Donation.user_id == user.id
                )
            )
        ).scalars().all()


donation_crud = CRUDReservation(Donation)
