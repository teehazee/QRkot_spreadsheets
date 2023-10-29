from sqlalchemy import CheckConstraint, Column, String, Text
from sqlalchemy.orm import declared_attr

from app.models.base import BaseModel


class CharityProject(BaseModel):
    @declared_attr
    def __table_args__(self) -> tuple:
        return (
            *super().__table_args__, CheckConstraint('length(name) > 0'),
            CheckConstraint('length(description) > 0'))

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return (
            f'{super().__repr__()},'
            f'name={self.name},'
            f'description={self.description}'
        )
