from sqlalchemy import Column, String, Text

from app.models.base import BaseModel


class CharityProject(BaseModel):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    def __repr__(self):
        return (
            f'name: {self.name[:16]}, '
            f'description: {self.description[:16]}, '
            f'{super().__repr__()}'
        )
