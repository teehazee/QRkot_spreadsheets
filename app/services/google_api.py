import copy
from datetime import datetime
from typing import Any, Dict, List, Tuple

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = '%Y/%m/%d %H:%M:%S'

VERSION_SHEETS = 'v4'

VERSION_DRIVE = 'v3'

ROW_COUNT = 100

COLUMN_COUNT = 11

HEADER = [
    ['Отчёт от', ''],
    ['Проекты по скорости закрытия'],
    ['Название проекта', 'Время сбора средств', 'Описание проекта']
]

TITLE = 'Отчёт приложения QRKot на {}'

SPREADSHEET_BODY = dict(
    properties=dict(
        locale='ru_RU',
    ),
    sheets=dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Проекты по скорости закрытия.',
        gridProperties=dict(
            rowCount=ROW_COUNT,
            columnCount=COLUMN_COUNT,
        )
    ))
)

SPREADSHEET_ERROR_MESSAGE = (
    'Передаваемые значения превышают созданные границы таблицы!'
    f'Число строк должно быть меньше {ROW_COUNT},'
    f'Число колонок должно быть меньше {COLUMN_COUNT}.'
)


def get_sorted_projects(projects: List) -> List[Tuple]:
    """Функция сортировки списка всех проектов."""
    return sorted(
        [
            (
                project.name,
                (project.close_date - project.create_date),
                project.description,
            )
            for project in projects
        ],
        key=lambda x: x[1]
    )


async def spreadsheets_create(wrapper_services: Aiogoogle,
                              spreadsheet_body: Dict = None,
                              ) -> Any:
    """Функция создания таблицы-отчёта в GD."""

    spreadsheet_body = (
        copy.deepcopy(SPREADSHEET_BODY) if spreadsheet_body is None
        else spreadsheet_body
    )
    spreadsheet_body['properties']['title'] = TITLE.format(
        datetime.now().strftime(FORMAT))
    service = await wrapper_services.discover(
        'sheets', VERSION_SHEETS)
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    """Функция предоставления прав доступа к аккаунту."""
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', VERSION_DRIVE)
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields='id'
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: List,
        wrapper_services: Aiogoogle
) -> None:
    """Функция записи полученной из БД информации в таблицу."""
    service = await wrapper_services.discover('sheets', VERSION_SHEETS)
    header = copy.deepcopy(HEADER)
    header[0][1] = str(datetime.utcnow())
    table_values = [
        *header,
        *[list(map(str, field)) for field in get_sorted_projects(projects)],
    ]
    rows = len(table_values)
    columns = max(map(len, table_values))
    if rows > ROW_COUNT or columns > COLUMN_COUNT:
        raise ValueError(
            SPREADSHEET_ERROR_MESSAGE.format(
                rows=rows, columns=columns
            )
        )

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows}C{columns}',
            valueInputOption='USER_ENTERED',
            json={
                'majorDimension': 'ROWS',
                'values': table_values
            }
        )
    )
