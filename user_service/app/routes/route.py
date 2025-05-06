from fastapi import APIRouter
from routes.auth import router as auth_router
from routes.user import router as user_router

# Create a central APIRouter instance to include all route modules
router = APIRouter()

# List of routers to include in the main application
router_list = [auth_router, user_router]

# Dynamically include all routers in the central APIRouter
for r in router_list:
    router.include_router(r)