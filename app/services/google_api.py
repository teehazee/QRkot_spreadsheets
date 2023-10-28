from copy import deepcopy
from datetime import datetime as dt

from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"

SPREADSHEET_HEAD = [
    ['Отчет от', ],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание проекта']
]

SHEET_ID = 0
ROW_COUNT = 100
COLUMN_COUNT = 11

SPREADSHEET_BODY = dict(
    properties=dict(
        title='Отчет на ',
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=SHEET_ID,
        title='Лист1',
        gridProperties=dict(
            rowCount=ROW_COUNT,
            columnCount=COLUMN_COUNT,
        )
    ))]
)

ERROR_ON_COUNT_ROWS_AND_COLUMNS = (
    'Ошибка! Передаваемые значения превышают созданные границы таблицы. '
    'Создано строк: {rows_create}, столбцов {columns_create}. '
    'Граница строк {rows_limit}, граница столбцов {columns_limit}.'
)


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = deepcopy(SPREADSHEET_BODY)
    spreadsheet_body['properties']['title'] += dt.now().strftime(FORMAT)
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = deepcopy(SPREADSHEET_HEAD)
    table_values[0].append(dt.now().strftime(FORMAT))
    table_values = [
        *table_values,
        *[list(map(str, [
               project.name,
               project.close_date - project.create_date,
               project.description
               ])) for project in charity_projects],
    ]
    rows = len(table_values)
    columns = max(len(columns) for columns in table_values)
    if rows > ROW_COUNT or columns > COLUMN_COUNT:
        raise ValueError(ERROR_ON_COUNT_ROWS_AND_COLUMNS.format(
            rows_create=ROW_COUNT,
            columns_create=COLUMN_COUNT,
            rows_limit=rows,
            columns_limit=columns
        ))

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows}C{columns}',
            valueInputOption='USER_ENTERED',
            json={
                'majorDimension': 'ROWS',
                'values': table_values}
        )
    )
