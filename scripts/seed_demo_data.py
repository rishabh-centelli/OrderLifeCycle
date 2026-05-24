import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.company import Company, CompanyType
from app.models.customer import Customer
from app.models.delivery import Delivery, DeliveryStatus
from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentMethod, TransactionStatus
from app.models.product import Product
from app.models.quote import Quote, QuoteStatus
from app.models.service_request import ServiceRequest, ServiceRequestStatus, ServiceRequestType
from app.models.user import User, UserRole


async def get_or_create(session, model, lookup: dict, values: dict):
    result = await session.execute(select(model).filter_by(**lookup))
    instance = result.scalar_one_or_none()
    if instance:
        return instance
    instance = model(**lookup, **values)
    session.add(instance)
    await session.flush()
    return instance


def money(value: str) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


async def main() -> None:
    async with AsyncSessionLocal() as session:
        admin = await get_or_create(
            session,
            User,
            {"email": "admin@example.com"},
            {
                "full_name": "Demo Admin",
                "hashed_password": hash_password("Admin@12345"),
                "role": UserRole.admin,
                "is_active": True,
            },
        )

        agent = await get_or_create(
            session,
            User,
            {"email": "agent@example.com"},
            {
                "full_name": "Demo UiPath Agent",
                "hashed_password": hash_password("Agent@12345"),
                "role": UserRole.agent,
                "is_active": True,
            },
        )

        cash_company = await get_or_create(
            session,
            Company,
            {"company_email": "accounts@cash-retail.example"},
            {
                "company_name": "Cash Retail Pvt Ltd",
                "gst_number": "27ABCDE1234F1Z5",
                "phone_no": "+91 98765 43210",
                "address": "Mumbai, Maharashtra",
                "type": CompanyType.cash,
            },
        )

        credit_company = await get_or_create(
            session,
            Company,
            {"company_email": "ap@credit-enterprise.example"},
            {
                "company_name": "Credit Enterprise Ltd",
                "gst_number": "29ABCDE1234F1Z7",
                "phone_no": "+91 98765 43211",
                "address": "Bengaluru, Karnataka",
                "type": CompanyType.credit,
            },
        )

        cash_customer = await get_or_create(
            session,
            Customer,
            {"email": "buyer@cash-retail.example"},
            {"company_id": cash_company.company_id, "customer_name": "Cash Buyer", "phone_no": "+91 90000 00001"},
        )

        await get_or_create(
            session,
            Customer,
            {"email": "procurement@credit-enterprise.example"},
            {
                "company_id": credit_company.company_id,
                "customer_name": "Credit Procurement",
                "phone_no": "+91 90000 00002",
            },
        )

        laptop = await get_or_create(
            session,
            Product,
            {"product_name": "Dell Latitude Laptop"},
            {
                "description": "Dell business laptop",
                "category": "Electronics",
                "unit_of_measure": "piece",
                "selling_price": money("50000.00"),
                "active_status": True,
            },
        )

        monitor = await get_or_create(
            session,
            Product,
            {"product_name": "24 Inch Monitor"},
            {
                "description": "Full HD office monitor",
                "category": "Electronics",
                "unit_of_measure": "piece",
                "selling_price": money("12000.00"),
                "active_status": True,
            },
        )

        await get_or_create(
            session,
            Inventory,
            {"product_id": laptop.product_id},
            {"available_quantity": 45, "reserved_quantity": 2, "reorder_level": 10},
        )
        await get_or_create(
            session,
            Inventory,
            {"product_id": monitor.product_id},
            {"available_quantity": 80, "reserved_quantity": 1, "reorder_level": 15},
        )

        quote_items = [
            {
                "item_id": 1,
                "product_id": str(laptop.product_id),
                "product_name": laptop.product_name,
                "description": laptop.description,
                "quantity": 2,
                "unit_price": "50000.00",
                "discount_amount": "5000.00",
                "tax_amount": "9000.00",
                "total_amount": "104000.00",
            }
        ]

        quote = await get_or_create(
            session,
            Quote,
            {"customer_id": cash_customer.customer_id, "quote_date": date.today()},
            {
                "valid_till": date.today() + timedelta(days=15),
                "status": QuoteStatus.approved,
                "notes": "Demo approved quote",
                "items": quote_items,
                "total_amount": money("104000.00"),
            },
        )

        order = await get_or_create(
            session,
            Order,
            {"quote_id": quote.quote_id},
            {
                "customer_id": cash_customer.customer_id,
                "order_date": date.today(),
                "expected_delivery_date": date.today() + timedelta(days=5),
                "order_status": OrderStatus.delivered,
                "payment_status": PaymentStatus.paid,
                "notes": "Demo delivered paid order",
                "items": quote_items,
                "total_amount": money("104000.00"),
            },
        )

        await get_or_create(
            session,
            Payment,
            {"transaction_reference": "DEMO-TXN-ORDER-001"},
            {
                "order_id": order.order_id,
                "payment_date": date.today(),
                "amount": money("104000.00"),
                "payment_method": PaymentMethod.bank_transfer,
                "payment_status": TransactionStatus.success,
                "remarks": "Demo full payment",
            },
        )

        await get_or_create(
            session,
            Delivery,
            {"tracking_number": "DEMO-TRACK-001"},
            {
                "order_id": order.order_id,
                "courier_name": "Demo Courier",
                "dispatch_date": date.today() - timedelta(days=3),
                "expected_delivery_date": date.today(),
                "delivered_date": date.today(),
                "delivery_status": DeliveryStatus.delivered,
                "attempt_count": 1,
                "last_attempt_date": date.today(),
                "failure_reason": None,
                "notes": "Demo successful delivery",
            },
        )

        service_items = [
            {
                "item_id": 1,
                "product_id": str(laptop.product_id),
                "product_name": laptop.product_name,
                "issue_description": "Screen flickering during startup",
                "quantity": 1,
                "requested_action": "replacement",
            }
        ]

        await get_or_create(
            session,
            ServiceRequest,
            {"order_id": order.order_id, "request_date": date.today()},
            {
                "customer_id": cash_customer.customer_id,
                "request_type": ServiceRequestType.replacement,
                "status": ServiceRequestStatus.open,
                "resolution_date": None,
                "resolution_notes": None,
                "items": service_items,
            },
        )

        await session.commit()
        print("Demo data seeded.")
        print("Admin login: admin@example.com / Admin@12345")
        print("Agent login: agent@example.com / Agent@12345")


if __name__ == "__main__":
    asyncio.run(main())
