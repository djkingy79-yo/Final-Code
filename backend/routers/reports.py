# DO NOT UNDO — reports router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Reports Router
Handles report generation, retrieval, and export (PDF/DOCX)
"""
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/cases/{case_id}/reports", tags=["reports"])


class ReportRequest(BaseModel):
    report_type: str  # quick_summary, full_detailed, extensive_log


# Note: The actual endpoints are still in server.py
# This router is prepared for future migration
# The report generation, PDF/DOCX export requires the full AI service and ReportLab integration
