from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.types import PositiveInt


class DonationCreate(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt


class DonationView(DonationCreate):
    user_id: Optional[int]
    invested_amount: Optional[int]
    fully_invested: Optional[bool]
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class DonationDB(DonationCreate):
    user_id: Optional[int]
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
