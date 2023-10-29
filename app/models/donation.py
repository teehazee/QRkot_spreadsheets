from sqlalchemy import Column, Integer, ForeignKey, Text

from .base import CharityDonationModel


class Donation(CharityDonationModel):
    """Модель Пожертвования."""

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    comment = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f'{super().__repr__()},'
            f'user_id={self.user_id},'
            f'comment={self.comment}'
        )
