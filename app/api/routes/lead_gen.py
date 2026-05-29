from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime
from app.database import get_db
from app.models.lead import Lead, LeadStatus, LeadSource
from app.services.nurture_engine import NurtureEngine

router = APIRouter(prefix="/api/lead-gen", tags=["Lead Generation"])


@router.get("/nurture/test")
async def test_nurture_email(
    email: str = "Stephen.trembley89@gmail.com",
    first_name: str = "Stephen",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Easy test endpoint - open this in browser to trigger a test nurture email.
    Example: /api/lead-gen/nurture/test?email=your@email.com
    """
    engine = NurtureEngine(db)

    custom_data = {
        "email": email,
        "first_name": first_name
    }

    background_tasks.add_task(engine.send_demo_followup, lead_id=1, custom_data=custom_data)

    return {
        "success": True,
        "message": f"Test nurture email triggered for {email}",
        "note": "Check your inbox in 1-2 minutes"
    }


# You can keep your other existing endpoints below this (linkedin, reddit, etc.)
# If you want the full file, let me know.