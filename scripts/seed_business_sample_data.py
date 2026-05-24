import asyncio
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.company import Company, CompanyType
from app.models.customer import Customer
from app.models.delivery import Delivery, DeliveryStatus
from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentMethod, TransactionStatus
from app.models.product import Product
from app.models.quote import Quote, QuoteStatus
from app.models.service_request import ServiceRequest, ServiceRequestStatus, ServiceRequestType


def stable_id(code: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"order-lifecycle/{code}")


def money(value: int | str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


async def upsert(session, model, pk_name: str, pk_value: UUID, values: dict):
    instance = await session.get(model, pk_value)
    if instance is None:
        instance = model(**{pk_name: pk_value}, **values)
        session.add(instance)
    else:
        for key, value in values.items():
            setattr(instance, key, value)
    await session.flush()
    return instance


async def main() -> None:
    company_1_id = stable_id("COMP001")
    company_2_id = stable_id("COMP002")
    customer_1_id = stable_id("CUST001")
    customer_2_id = stable_id("CUST002")
    product_1_id = stable_id("PROD001")
    product_2_id = stable_id("PROD002")
    inventory_1_id = stable_id("INV001")
    inventory_2_id = stable_id("INV002")
    quote_1_id = stable_id("QUO001")
    order_1_id = stable_id("ORD001")
    payment_1_id = stable_id("PAY001")
    delivery_1_id = stable_id("DEL001")
    request_1_id = stable_id("SR001")

    quote_items = [
        {
            "item_id": 1,
            "source_product_code": "PROD001",
            "product_id": str(product_1_id),
            "product_name": "Dell Latitude Laptop",
            "quantity": 15,
            "unit_price": "62000.00",
            "discount_amount": "30000.00",
            "tax_amount": "167400.00",
            "total_amount": "1067400.00",
        }
    ]

    order_items = [
        {
            "item_id": 1,
            "source_product_code": "PROD001",
            "product_id": str(product_1_id),
            "product_name": "Dell Latitude Laptop",
            "quantity": 15,
            "unit_price": "62000.00",
            "tax_amount": "167400.00",
            "total_amount": "1067400.00",
        }
    ]

    service_items = [
        {
            "item_id": 1,
            "source_product_code": "PROD001",
            "product_id": str(product_1_id),
            "product_name": "Dell Latitude Laptop",
            "issue_description": "Screen flickering",
            "quantity": 1,
            "requested_action": "replacement",
        }
    ]

    async with AsyncSessionLocal() as session:
        await upsert(
            session,
            Company,
            "company_id",
            company_1_id,
            {
                "company_name": "ABC Technologies Pvt Ltd",
                "company_email": "procurement@abctech.com",
                "gst_number": "29ABCDE1234F1Z5",
                "phone_no": "9876543210",
                "address": "Bangalore, Karnataka",
                "type": CompanyType.credit,
            },
        )
        await upsert(
            session,
            Company,
            "company_id",
            company_2_id,
            {
                "company_name": "NextGen Solutions",
                "company_email": "orders@nextgen.com",
                "gst_number": "07PQRSX5678L1Z2",
                "phone_no": "9123456780",
                "address": "Delhi, India",
                "type": CompanyType.cash,
            },
        )

        await upsert(
            session,
            Customer,
            "customer_id",
            customer_1_id,
            {
                "company_id": company_1_id,
                "customer_name": "Rahul Sharma",
                "email": "rahul@abctech.com",
                "phone_no": "9999999999",
            },
        )
        await upsert(
            session,
            Customer,
            "customer_id",
            customer_2_id,
            {
                "company_id": company_2_id,
                "customer_name": "Amit Verma",
                "email": "amit@nextgen.com",
                "phone_no": "8888888888",
            },
        )

        await upsert(
            session,
            Product,
            "product_id",
            product_1_id,
            {
                "product_name": "Dell Latitude Laptop",
                "description": "Dell Latitude 5440",
                "category": "Laptop",
                "unit_of_measure": "Piece",
                "selling_price": money(65000),
                "active_status": True,
            },
        )
        await upsert(
            session,
            Product,
            "product_id",
            product_2_id,
            {
                "product_name": "24 Inch Monitor",
                "description": "Dell 24 inch monitor",
                "category": "Monitor",
                "unit_of_measure": "Piece",
                "selling_price": money(12000),
                "active_status": True,
            },
        )

        await upsert(
            session,
            Inventory,
            "inventory_id",
            inventory_1_id,
            {
                "product_id": product_1_id,
                "available_quantity": 50,
                "reserved_quantity": 5,
                "reorder_level": 10,
            },
        )
        await upsert(
            session,
            Inventory,
            "inventory_id",
            inventory_2_id,
            {
                "product_id": product_2_id,
                "available_quantity": 100,
                "reserved_quantity": 10,
                "reorder_level": 20,
            },
        )

        await upsert(
            session,
            Quote,
            "quote_id",
            quote_1_id,
            {
                "customer_id": customer_1_id,
                "quote_date": date.fromisoformat("2026-05-24"),
                "valid_till": date.fromisoformat("2026-05-31"),
                "status": QuoteStatus.sent,
                "notes": "Bulk pricing applied",
                "items": quote_items,
                "total_amount": money(1067400),
            },
        )

        await upsert(
            session,
            Order,
            "order_id",
            order_1_id,
            {
                "customer_id": customer_1_id,
                "quote_id": quote_1_id,
                "order_date": date.fromisoformat("2026-05-25"),
                "expected_delivery_date": date.fromisoformat("2026-05-30"),
                "order_status": OrderStatus.confirmed,
                "payment_status": PaymentStatus.partial,
                "notes": "Priority delivery",
                "items": order_items,
                "total_amount": money(1067400),
            },
        )

        await upsert(
            session,
            Payment,
            "payment_id",
            payment_1_id,
            {
                "order_id": order_1_id,
                "payment_date": date.fromisoformat("2026-05-25"),
                "amount": money(500000),
                "payment_method": PaymentMethod.bank_transfer,
                "transaction_reference": "TXN987654",
                "payment_status": TransactionStatus.success,
                "remarks": "Advance payment received",
            },
        )

        await upsert(
            session,
            Delivery,
            "delivery_id",
            delivery_1_id,
            {
                "order_id": order_1_id,
                "tracking_number": "TRK123456",
                "courier_name": "Delhivery",
                "dispatch_date": date.fromisoformat("2026-05-26"),
                "expected_delivery_date": date.fromisoformat("2026-05-30"),
                "delivered_date": None,
                "delivery_status": DeliveryStatus.in_transit,
                "attempt_count": 0,
                "last_attempt_date": None,
                "failure_reason": None,
                "notes": None,
            },
        )

        await upsert(
            session,
            ServiceRequest,
            "request_id",
            request_1_id,
            {
                "order_id": order_1_id,
                "customer_id": customer_1_id,
                "request_date": date.fromisoformat("2026-06-02"),
                "request_type": ServiceRequestType.replacement,
                "status": ServiceRequestStatus.open,
                "resolution_date": None,
                "resolution_notes": "",
                "items": service_items,
            },
        )

        await session.commit()

        print("Business sample data seeded.")
        print("Source codes were mapped to stable UUID primary keys:")
        for code in [
            "COMP001",
            "COMP002",
            "CUST001",
            "CUST002",
            "PROD001",
            "PROD002",
            "QUO001",
            "ORD001",
            "PAY001",
            "DEL001",
            "SR001",
        ]:
            print(f"{code}: {stable_id(code)}")


if __name__ == "__main__":
    asyncio.run(main())
