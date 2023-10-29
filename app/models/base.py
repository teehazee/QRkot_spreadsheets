from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer
)

from app.core.db import Base


class CharityDonationModel(Base):
    """Абстрактная модель."""

    __abstract__ = True

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime, nullable=True, default=None)

    __table_args__ = (
        CheckConstraint(
            'full_amount > 0', name='check_full_amount_zero'
        ),
        CheckConstraint(
            'full_amount >= invested_amount', name='check_full_amount_more_invested_amount'
        ),
        CheckConstraint(
            'invested_amount >= 0', name='check_invested_amount_more_zero'))

    def __repr__(self) -> str:
        return (
            f'full_amount={self.full_amount},'
            f'invested_amount={self.invested_amount},'
            f'fully_invested={self.fully_invested},'
            f'create_date={self.create_date},'
            f'close_date={self.close_date}'
        )
