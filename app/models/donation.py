from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseModel


class Donation(BaseModel):
    user_id = Column(Integer, ForeignKey(
        'user.id',
        name='fk_donation_user_id_user'
    ))
    comment = Column(Text)

    def __repr__(self):
        return (
            f'user_id: {self.user_id}, '
            f'comment: {self.comment[:8]} , '
            f'{super().__repr__()}'
        )
