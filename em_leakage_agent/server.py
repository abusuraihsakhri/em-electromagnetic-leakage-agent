"""
FastAPI REST API Server for Screaming Channels: RF / Electromagnetic Cryptographic Leakage Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import EMLeakageCoordinator

coordinator = EMLeakageCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field, field_validator
        import math

        app = FastAPI(
            title="Screaming Channels: RF / Electromagnetic Cryptographic Leakage Agent",
            description="Evaluates mixed-signal SoC radio frequency transmitter phase noise and unintended EM side-channel radiation profiles.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = Field(default_factory=dict)

            @field_validator("primary_metric", "secondary_metric")
            @classmethod
            def reject_non_finite(cls, value: float):
                if not math.isfinite(value):
                    raise ValueError("Metric must be finite")
                return value

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "em-electromagnetic-leakage-agent", "domain": "Hardware Security", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
