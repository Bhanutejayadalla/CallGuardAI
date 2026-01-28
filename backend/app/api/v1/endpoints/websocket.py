"""
WebSocket Endpoints for Real-time Analysis
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import json
import uuid
import asyncio
import base64
from datetime import datetime
from typing import Dict, List

from app.core.database import get_db
from app.services.analysis_service import AnalysisService
from app.models.call import Call, CallStatus, CallClassification

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.analysis_sessions: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.analysis_sessions[client_id] = {
            "audio_chunks": [],
            "partial_transcript": "",
            "current_risk": 0,
            "flags": [],
            "start_time": datetime.utcnow()
        }
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.analysis_sessions:
            del self.analysis_sessions[client_id]
        logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/stream/{client_id}")
async def websocket_stream_analysis(
    websocket: WebSocket,
    client_id: str
):
    """
    WebSocket endpoint for real-time audio streaming and analysis
    
    Protocol:
    - Client sends audio chunks as base64 encoded data
    - Server responds with partial analysis results
    - Final analysis sent when client signals end of stream
    """
    await manager.connect(websocket, client_id)
    
    analysis_service = AnalysisService()
    call_id = f"stream_{uuid.uuid4().hex[:12]}"
    
    try:
        # Send connection confirmation
        await manager.send_message(client_id, {
            "type": "connected",
            "call_id": call_id,
            "message": "Ready for audio stream"
        })
        
        accumulated_text = ""
        chunk_count = 0
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "audio_chunk":
                chunk_count += 1
                audio_data = message.get("data", "")
                is_final = message.get("is_final", False)
                
                # Process chunk
                result = await analysis_service.process_stream_chunk(
                    audio_data,
                    accumulated_text,
                    chunk_count
                )
                
                accumulated_text = result.get("transcript", accumulated_text)
                
                # Send partial result
                await manager.send_message(client_id, {
                    "type": "partial_result",
                    "chunk_id": chunk_count,
                    "partial_transcript": result.get("new_text", ""),
                    "current_risk_score": result.get("risk_score", 0),
                    "detected_flags": result.get("flags", []),
                    "is_processing": not is_final
                })
                
                if is_final:
                    # Perform final analysis
                    final_result = await analysis_service.analyze_text(
                        accumulated_text,
                        call_id
                    )
                    
                    await manager.send_message(client_id, {
                        "type": "final_result",
                        "call_id": call_id,
                        "result": {
                            "classification": final_result.classification,
                            "risk_score": final_result.risk_score,
                            "transcript": final_result.transcript,
                            "suspicious_keywords": final_result.suspicious_keywords,
                            "fraud_indicators": final_result.fraud_indicators,
                            "ai_explanation": final_result.ai_explanation,
                            "voice_characteristics": final_result.voice_characteristics,
                            "confidence_score": final_result.confidence_score
                        }
                    })
                    break
            
            elif message.get("type") == "text_chunk":
                # Direct text analysis (without audio)
                text = message.get("text", "")
                accumulated_text += " " + text
                
                # Quick analysis
                result = await analysis_service.quick_text_analysis(accumulated_text)
                
                await manager.send_message(client_id, {
                    "type": "text_analysis",
                    "current_risk_score": result.get("risk_score", 0),
                    "detected_flags": result.get("flags", []),
                    "suspicious_keywords": result.get("keywords", [])
                })
            
            elif message.get("type") == "ping":
                await manager.send_message(client_id, {"type": "pong"})
            
            elif message.get("type") == "end":
                break
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.send_message(client_id, {
            "type": "error",
            "message": str(e)
        })
    
    finally:
        manager.disconnect(client_id)


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications
    """
    await websocket.accept()
    client_id = f"alert_{uuid.uuid4().hex[:8]}"
    
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(5)
            
            # In production, this would check for new alerts
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except WebSocketDisconnect:
        logger.info(f"Alert client {client_id} disconnected")


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates
    """
    await websocket.accept()
    
    try:
        while True:
            # Send periodic dashboard updates
            await asyncio.sleep(10)
            
            # In production, this would fetch real stats
            await websocket.send_json({
                "type": "dashboard_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "active_analyses": 0,
                    "recent_alerts": []
                }
            })
    
    except WebSocketDisconnect:
        pass
