from fastapi import APIRouter
from app.api.v1.endpoints import (
    graph,
)

api_router = APIRouter()
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
