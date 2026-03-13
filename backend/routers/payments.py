# DO NOT UNDO — payments router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Payments Router
Handles PayPal integration for premium features
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import logging

from config import db, logger
from auth_utils import get_current_user, verify_case_ownership

router = APIRouter(prefix="/api", tags=["payments"])


class PaymentOrder(BaseModel):
    feature_type: str  # grounds_details, full_report, extensive_report
    amount: float
    currency: str = "AUD"


# Feature prices
FEATURE_PRICES = {
    "grounds_details": 50.00,
    "full_report": 29.00,
    "extensive_report": 39.00
}


# Note: The actual endpoints are still in server.py
# This router is prepared for future migration
# The PayPal integration requires the full webhook handling
