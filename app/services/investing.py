from datetime import datetime
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel


async def investation(
        obj_in: BaseModel,
        opposing_model: Type[BaseModel],
        session: AsyncSession,
) -> BaseModel:
    open_objs = await session.execute(select(opposing_model).where(
        opposing_model.fully_invested == False  # noqa
    ).order_by(opposing_model.create_date))
    open_objs = open_objs.scalars().all()
    for obj in open_objs:
        obj_in, obj = await calculation(obj_in, obj)
        session.add(obj_in)
        session.add(obj)
    await session.commit()
    await session.refresh(obj_in)
    return obj_in


async def close_obj(obj: BaseModel) -> BaseModel:
    obj.invested_amount = obj.full_amount
    obj.fully_invested = True
    obj.close_date = datetime.now()
    return obj


async def calculation(obj_in, obj):
    amount_money_have = obj_in.full_amount - obj_in.invested_amount
    amount_money_need = obj.full_amount - obj.invested_amount
    if amount_money_have == amount_money_need:
        obj_in = await close_obj(obj_in)
        obj = await close_obj(obj)
    elif amount_money_have > amount_money_need:
        obj_in.invested_amount += amount_money_need
        obj = await close_obj(obj)
    else:
        obj.invested_amount += amount_money_have
        obj_in = await close_obj(obj_in)
    return obj_in, obj
