from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationView(DonationCreate):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationView):
    user_id: Optional[int]
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
