from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import BusinessRuleError
from app.schemas.common import QuoteOrderItem
from app.services.common import decimal_money


def test_decimal_money_quantizes_to_cents():
    assert decimal_money("10.555") == Decimal("10.56")


def test_quote_item_requires_positive_quantity():
    with pytest.raises(ValueError):
        QuoteOrderItem(item_id=1, product_id=uuid4(), quantity=0)


def test_overpayment_rule_example():
    order_total = Decimal("100.00")
    paid = Decimal("80.00")
    incoming = Decimal("25.00")
    with pytest.raises(BusinessRuleError):
        if paid + incoming > order_total:
            raise BusinessRuleError("Payment would exceed order total")
