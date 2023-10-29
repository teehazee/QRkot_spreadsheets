from datetime import datetime
from typing import List

from app.models.base import CharityDonationModel


def investation(
    target: CharityDonationModel,
    sources: List[CharityDonationModel]
) -> List[CharityDonationModel]:
    """Функция инвестирования."""
    results: list = []
    if not target.invested_amount:
        target.invested_amount = 0
    for source in sources:
        results.append(source)
        to_invest = min(
            source.full_amount - source.invested_amount,
            target.full_amount - target.invested_amount
        )
        for obj in (target, source):
            obj.invested_amount += to_invest
            if obj.full_amount == obj.invested_amount:
                obj.close_date = datetime.now()
                obj.fully_invested = True
        if target.fully_invested:
            break
    return results
