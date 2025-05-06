from fastapi import APIRouter
from routes.post import router as post_router

# Create a central APIRouter instance to include all route modules
router = APIRouter()

# List of routers to include in the main application
router_list = [post_router]

# Dynamically include all routers in the central APIRouter
for r in router_list:
    router.include_router(r)