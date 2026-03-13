# DO NOT UNDO — grounds router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Grounds of Merit Router
Handles grounds of merit CRUD, AI identification, and investigation
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import logging

from config import db, logger
from auth_utils import get_current_user, verify_case_ownership

router = APIRouter(prefix="/api/cases/{case_id}/grounds", tags=["grounds"])


class GroundOfMeritCreate(BaseModel):
    title: str
    ground_type: str
    description: str
    strength: str = "moderate"
    supporting_evidence: List[str] = []


class GroundOfMeritUpdate(BaseModel):
    title: Optional[str] = None
    ground_type: Optional[str] = None
    description: Optional[str] = None
    strength: Optional[str] = None
    status: Optional[str] = None
    supporting_evidence: Optional[List[str]] = None


# Note: The actual endpoints are still in server.py
# This router is prepared for future migration
# The AI identification and investigation logic requires the full AI service integration
