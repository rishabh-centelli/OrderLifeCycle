from fastapi import APIRouter

from app.api.v1 import auth, companies, customers, deliveries, orders, payments, products, quotes, service_requests

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(customers.router)
api_router.include_router(products.router)
api_router.include_router(quotes.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(deliveries.router)
api_router.include_router(service_requests.router)
