# DO NOT UNDO — analytics router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Analytics Router
Provides comprehensive usage statistics and metrics
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta

from config import db, logger, get_admin_emails
from auth_utils import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Admin emails
ADMIN_EMAILS = get_admin_emails()


@router.post("/track-visit")
async def track_visit(request: Request):
    """Track a page visit (public endpoint)"""
    try:
        # Get visitor info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        referer = request.headers.get("referer", "")
        
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Create a simple fingerprint for unique visitor tracking
        visitor_id = f"{client_ip}_{user_agent[:50]}"
        
        # Check if this visitor already visited today
        existing_visit = await db.visits.find_one({
            "visitor_id": visitor_id,
            "date": today
        })
        
        if not existing_visit:
            # New visitor today - record the visit
            await db.visits.insert_one({
                "visitor_id": visitor_id,
                "ip": client_ip,
                "user_agent": user_agent[:200],
                "referer": referer[:500] if referer else "",
                "date": today,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Update daily counter
            await db.visit_stats.update_one(
                {"date": today},
                {"$inc": {"count": 1, "unique_visitors": 1}},
                upsert=True
            )
            
            # Update total counter
            await db.counters.update_one(
                {"name": "total_visitors"},
                {"$inc": {"count": 1}},
                upsert=True
            )
        
        return {"status": "tracked"}
        
    except Exception as e:
        logger.error(f"Visit tracking error: {e}")
        return {"status": "error"}


@router.get("/visitor-count")
async def get_visitor_count():
    """Get public visitor count (no auth required)"""
    try:
        # Get total unique visitors
        total_counter = await db.counters.find_one({"name": "total_visitors"}, {"_id": 0})
        total_visitors = total_counter["count"] if total_counter else 0
        
        # Get today's visitors
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_stats = await db.visit_stats.find_one({"date": today}, {"_id": 0})
        today_visitors = today_stats["unique_visitors"] if today_stats else 0
        
        # Get registered users count
        total_users = await db.users.count_documents({})
        
        # Get total cases
        total_cases = await db.cases.count_documents({})
        
        return {
            "total_visitors": total_visitors,
            "today_visitors": today_visitors,
            "registered_users": total_users,
            "cases_created": total_cases
        }
        
    except Exception as e:
        logger.error(f"Visitor count error: {e}")
        return {
            "total_visitors": 0,
            "today_visitors": 0,
            "registered_users": 0,
            "cases_created": 0
        }


@router.get("/dashboard")
async def get_dashboard_stats(request: Request):
    """Get comprehensive dashboard statistics (admin only)"""
    try:
        user = await get_current_user(request)
        
        # Only allow admin emails
        if user.email not in ADMIN_EMAILS:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Calculate date ranges
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # === USER METRICS ===
        total_users = await db.users.count_documents({})
        
        # New users in last 7 days
        new_users_7d = await db.users.count_documents({
            "created_at": {"$gte": week_ago.isoformat()}
        })
        
        # New users in last 30 days
        new_users_30d = await db.users.count_documents({
            "created_at": {"$gte": month_ago.isoformat()}
        })
        
        # Users by auth type
        email_users = await db.users.count_documents({"auth_type": "email"})
        google_users = await db.users.count_documents({"auth_type": "google"})
        
        # === CASE METRICS ===
        total_cases = await db.cases.count_documents({})
        
        # Cases created in last 7 days
        new_cases_7d = await db.cases.count_documents({
            "created_at": {"$gte": week_ago.isoformat()}
        })
        
        # Cases created in last 30 days
        new_cases_30d = await db.cases.count_documents({
            "created_at": {"$gte": month_ago.isoformat()}
        })
        
        # Cases by state
        cases_by_state = {}
        states = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]
        for state in states:
            count = await db.cases.count_documents({"state": state})
            if count > 0:
                cases_by_state[state.upper()] = count
        
        # === DOCUMENT METRICS ===
        total_documents = await db.documents.count_documents({})
        documents_7d = await db.documents.count_documents({
            "uploaded_at": {"$gte": week_ago.isoformat()}
        })
        
        # === ACTIVITY METRICS ===
        total_visits = await db.visits.count_documents({})
        visits_7d = await db.visits.count_documents({
            "timestamp": {"$gte": week_ago.isoformat()}
        })
        visits_30d = await db.visits.count_documents({
            "timestamp": {"$gte": month_ago.isoformat()}
        })
        
        # === ENGAGEMENT METRICS ===
        # Reports generated
        total_reports = await db.reports.count_documents({}) if "reports" in await db.list_collection_names() else 0
        
        # Deadlines tracked
        total_deadlines = await db.deadlines.count_documents({})
        
        # Notes created
        total_notes = await db.notes.count_documents({})
        
        # Contact messages
        total_messages = await db.contact_messages.count_documents({})
        unread_messages = await db.contact_messages.count_documents({"read": False})
        
        # Success stories submitted
        total_stories = await db.success_stories.count_documents({})
        
        # === DAILY STATS FOR CHART (Last 30 days) ===
        daily_stats = []
        for i in range(30, -1, -1):
            date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            
            # Users registered on this day
            users_on_day = await db.users.count_documents({
                "created_at": {
                    "$gte": f"{date}T00:00:00",
                    "$lt": f"{date}T23:59:59"
                }
            })
            
            # Cases created on this day
            cases_on_day = await db.cases.count_documents({
                "created_at": {
                    "$gte": f"{date}T00:00:00",
                    "$lt": f"{date}T23:59:59"
                }
            })
            
            # Visits on this day
            visit_stat = await db.visit_stats.find_one({"date": date}, {"_id": 0})
            visits_on_day = visit_stat["count"] if visit_stat else 0
            
            daily_stats.append({
                "date": date,
                "users": users_on_day,
                "cases": cases_on_day,
                "visits": visits_on_day
            })
        
        # === RESPONSE ===
        return {
            "users": {
                "total": total_users,
                "new_7d": new_users_7d,
                "new_30d": new_users_30d,
                "by_auth_type": {
                    "email": email_users,
                    "google": google_users
                }
            },
            "cases": {
                "total": total_cases,
                "new_7d": new_cases_7d,
                "new_30d": new_cases_30d,
                "by_state": cases_by_state
            },
            "documents": {
                "total": total_documents,
                "uploaded_7d": documents_7d
            },
            "engagement": {
                "reports_generated": total_reports,
                "deadlines_tracked": total_deadlines,
                "notes_created": total_notes,
                "contact_messages": total_messages,
                "unread_messages": unread_messages,
                "success_stories": total_stories
            },
            "visits": {
                "total": total_visits,
                "last_7d": visits_7d,
                "last_30d": visits_30d
            },
            "daily_stats": daily_stats,
            "generated_at": now.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

@router.get("/quick-stats")
async def get_quick_stats(request: Request):
    """Get quick overview stats (admin only)"""
    try:
        user = await get_current_user(request)
        
        if user.email not in ADMIN_EMAILS:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        total_users = await db.users.count_documents({})
        total_cases = await db.cases.count_documents({})
        total_visits = await db.visits.count_documents({})
        unread_messages = await db.contact_messages.count_documents({"read": False})
        
        return {
            "total_users": total_users,
            "total_cases": total_cases,
            "total_visits": total_visits,
            "unread_messages": unread_messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quick stats")
