# app/routes/__init__.py

from fastapi import APIRouter
from .auth_routes import router as auth_router
from .user_routes import router as users_router
from .vehicle_routes import router as vehicles_router
from .qb_routes import router as qb_router
from .jobs_routes import router as jobs_router

router = APIRouter()

router.include_router(auth_router, prefix="/api", tags=["Auth"])
router.include_router(users_router, prefix="/api/users", tags=["Users"])
router.include_router(vehicles_router, prefix="/api/vehicles", tags=["Vehicles"])
router.include_router(qb_router, prefix="/api/qb", tags=["QuickBooks"])
router.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])  