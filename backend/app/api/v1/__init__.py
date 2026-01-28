"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import analyze, calls, analytics, admin, auth, websocket, ai_voice

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
api_router.include_router(ai_voice.router, prefix="/ai-voice", tags=["AI Voice Detection"])
api_router.include_router(calls.router, prefix="/calls", tags=["Calls"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
