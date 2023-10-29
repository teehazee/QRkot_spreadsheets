from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class CharityProjectBase(BaseModel):
    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., max_length=100)
    description: str
    full_amount: PositiveInt = Field(..., example=100)

    class Config:
        min_anystr_length = 1
        schema_extra = {
            'example': {
                'name': 'Василий',
                'description': 'На печеньки',
                'full_amount': 750
            }
        }


class CharityProjectUpdate(CharityProjectBase):
    name: str = Field(None, min_length=1, max_length=100)
    description: Optional[str]
    full_amount: Optional[PositiveInt] = Field(example=100)

    class Config:
        min_anystr_length = 1
        extra = Extra.forbid
        schema_extra = {
            'example': {
                'name': 'Степан',
                'description': 'На корм',
                'full_amount': 1500
            }
        }


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: datetime = datetime.utcnow()
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
