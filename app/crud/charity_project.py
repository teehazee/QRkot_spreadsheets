from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CrudCharityProject(CRUDBase):

    @staticmethod
    async def get_charity_project_name(
            charity_project_name: str,
            session: AsyncSession,
    ) -> Optional[CharityProject]:
        db_charity_project = await session.execute(
            select(CharityProject).where(
                CharityProject.name == charity_project_name
            )
        )
        return db_charity_project.scalars().first()


charity_project_crud = CrudCharityProject(CharityProject)
