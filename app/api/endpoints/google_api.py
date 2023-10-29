from typing import Any, Dict

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.google_api import (
    set_user_permissions,
    spreadsheets_create,
    spreadsheets_update_value
)

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(current_superuser)]
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)
) -> Dict[str, Any]:
    """Создание отчёта в Google таблицах.
       В отчёте: закрытые проекты, отсортированные по времени, затраченному на
       сборы средств.
       Только для суперюзеров.
    """
    projects = await charity_project_crud.get_fully_invested(
        session
    )
    try:
        spreadsheet_id, spreadsheet_url = await spreadsheets_create(wrapper_services)
        await set_user_permissions(spreadsheet_id, wrapper_services)
        await spreadsheets_update_value(
            spreadsheet_id, projects, wrapper_services
        )
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(error))
    return dict(doc=spreadsheet_url)
