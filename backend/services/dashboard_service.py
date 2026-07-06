"""Dashboard service — weekly progress aggregation from Cloudant."""

import structlog
from datetime import date, timedelta, datetime, timezone
from typing import Optional, List

from backend.api.config import settings
from backend.database.cloudant import cloudant_client
from backend.models.dashboard import DailyEntry, DashboardResponse, WeeklySummary, GoalTargets

logger = structlog.get_logger(__name__)

_PROGRESS_DB = settings.CLOUDANT_DB_PROGRESS


def _get_weekly_entries(user_id: str, week_start: date) -> list[DailyEntry]:
    """
    Fetch all daily progress entries for a user in the given 7-day window.

    Returns a list of DailyEntry objects — one per day that has a record.
    Missing days are not padded; the frontend handles gaps.
    """
    week_end = week_start + timedelta(days=6)
    result = cloudant_client.post_find(
        db=_PROGRESS_DB,
        selector={
            "user_id": {"$eq": user_id},
            "date": {
                "$gte": week_start.isoformat(),
                "$lte": week_end.isoformat(),
            },
        },
        limit=7,
    ).get_result()

    entries: list[DailyEntry] = []
    for doc in result.get("docs", []):
        entries.append(
            DailyEntry(
                date=date.fromisoformat(doc["date"]),
                calories_consumed=int(doc.get("calories_consumed", 0)),
                protein_g=float(doc.get("protein_g", 0.0)),
                water_ml=int(doc.get("water_ml", 0)),
                weight_kg=doc.get("weight_kg"),
                meals=doc.get("meals"),
                feedback_rating=doc.get("feedback_rating"),
                feedback_comment=doc.get("feedback_comment"),
            )
        )

    entries.sort(key=lambda e: e.date)
    return entries


def _compute_summary(entries: list[DailyEntry]) -> WeeklySummary:
    """Compute aggregated stats from a list of daily entries."""
    if not entries:
        return WeeklySummary(
            avg_calories=0.0,
            avg_protein_g=0.0,
            avg_water_ml=0.0,
            weight_change_kg=None,
            goal_adherence_percent=0.0,
        )

    n = len(entries)
    avg_cal = sum(e.calories_consumed for e in entries) / n
    avg_pro = sum(e.protein_g for e in entries) / n
    avg_water = sum(e.water_ml for e in entries) / n

    weights = [e.weight_kg for e in entries if e.weight_kg is not None]
    weight_change = (weights[-1] - weights[0]) if len(weights) >= 2 else None

    # Goal adherence: % of days with at least one entry (simple proxy)
    adherence = (n / 7) * 100

    return WeeklySummary(
        avg_calories=round(avg_cal, 1),
        avg_protein_g=round(avg_pro, 1),
        avg_water_ml=round(avg_water, 1),
        weight_change_kg=round(weight_change, 2) if weight_change is not None else None,
        goal_adherence_percent=round(adherence, 1),
    )


def _build_charts_data(entries: list[DailyEntry]) -> dict:
    """Build recharts-compatible series arrays from daily entries."""
    return {
        "calories": [
            {"date": e.date.isoformat(), "value": e.calories_consumed} for e in entries
        ],
        "protein": [
            {"date": e.date.isoformat(), "value": round(e.protein_g, 1)} for e in entries
        ],
        "water": [
            {"date": e.date.isoformat(), "value": round(e.water_ml / 1000, 2)} for e in entries
        ],
        "weight": [
            {"date": e.date.isoformat(), "value": e.weight_kg}
            for e in entries
            if e.weight_kg is not None
        ],
    }


def _get_or_create_daily_doc(user_id: str, log_date: date) -> dict:
    """Fetch an existing daily progress document from Cloudant or create a new one."""
    doc_id = f"{user_id}:{log_date.isoformat()}"
    try:
        doc = cloudant_client.get_document(db=_PROGRESS_DB, doc_id=doc_id).get_result()
    except Exception:
        # Create a new blank doc template for this day
        doc = {
            "_id": doc_id,
            "user_id": user_id,
            "date": log_date.isoformat(),
            "calories_consumed": 0,
            "protein_g": 0.0,
            "water_ml": 0,
            "weight_kg": None,
            "meals": [],
            "feedback_rating": None,
            "feedback_comment": None,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
        }
    return doc


def log_meal(
    user_id: str,
    log_date: date,
    meal_type: str,
    name: str,
    calories: int,
    protein_g: float,
) -> dict:
    """Log a meal to the daily progress document in Cloudant."""
    doc = _get_or_create_daily_doc(user_id, log_date)

    meals = doc.get("meals", [])
    if meals is None:
        meals = []
    meals.append({
        "type": meal_type,
        "name": name,
        "calories": calories,
        "protein_g": protein_g,
        "logged_at": datetime.now(tz=timezone.utc).isoformat()
    })
    doc["meals"] = meals

    # Update running totals
    doc["calories_consumed"] = int(doc.get("calories_consumed", 0)) + calories
    doc["protein_g"] = float(doc.get("protein_g", 0.0)) + protein_g
    doc["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    cloudant_client.put_document(db=_PROGRESS_DB, doc_id=doc["_id"], document=doc)
    logger.info("Meal logged successfully", user_id=user_id, date=log_date.isoformat(), meal=name)
    return doc


def log_water(user_id: str, log_date: date, amount_ml: int) -> dict:
    """Log water intake to the daily progress document in Cloudant."""
    doc = _get_or_create_daily_doc(user_id, log_date)
    doc["water_ml"] = int(doc.get("water_ml", 0)) + amount_ml
    doc["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    cloudant_client.put_document(db=_PROGRESS_DB, doc_id=doc["_id"], document=doc)
    logger.info("Water intake logged", user_id=user_id, date=log_date.isoformat(), amount_ml=amount_ml)
    return doc


def log_weight(user_id: str, log_date: date, weight_kg: float) -> dict:
    """Log weight to the daily progress document and sync it with user profile."""
    doc = _get_or_create_daily_doc(user_id, log_date)
    doc["weight_kg"] = weight_kg
    doc["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    cloudant_client.put_document(db=_PROGRESS_DB, doc_id=doc["_id"], document=doc)

    # Sync weight to user profile
    try:
        from backend.services.user_service import get_user_by_id
        user_doc = get_user_by_id(user_id)
        if user_doc:
            user_doc["weight_kg"] = weight_kg
            user_doc["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
            cloudant_client.put_document(db=settings.CLOUDANT_DB_USERS, doc_id=user_id, document=user_doc)
            logger.info("Weight synced to user profile", user_id=user_id, weight_kg=weight_kg)
    except Exception as e:
        logger.error("Failed to sync weight to user profile", error=str(e))

    logger.info("Weight logged", user_id=user_id, date=log_date.isoformat(), weight_kg=weight_kg)
    return doc


def log_feedback(user_id: str, log_date: date, rating: int, comment: Optional[str] = None) -> dict:
    """Log daily feedback to the daily progress document and also to dedicated feedback DB."""
    doc = _get_or_create_daily_doc(user_id, log_date)
    doc["feedback_rating"] = rating
    doc["feedback_comment"] = comment
    doc["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    cloudant_client.put_document(db=_PROGRESS_DB, doc_id=doc["_id"], document=doc)

    # Log to dedicated feedback DB
    try:
        feedback_id = f"{user_id}:{log_date.isoformat()}:feedback"
        feedback_doc = {
            "_id": feedback_id,
            "user_id": user_id,
            "date": log_date.isoformat(),
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now(tz=timezone.utc).isoformat()
        }
        cloudant_client.put_document(db=settings.CLOUDANT_DB_FEEDBACK, doc_id=feedback_id, document=feedback_doc)
        logger.info("Feedback persisted in dedicated database", user_id=user_id, rating=rating)
    except Exception as e:
        logger.error("Failed to persist feedback in dedicated database", error=str(e))

    logger.info("Daily feedback logged", user_id=user_id, date=log_date.isoformat(), rating=rating)
    return doc


def get_user_goals(user_id: str) -> GoalTargets:
    """Dynamically calculate calorie, protein, and water targets from user profile."""
    try:
        from backend.services.user_service import get_user_by_id
        from backend.services.meal_plan_service import calculate_tdee

        user_doc = get_user_by_id(user_id)
        if user_doc and all(k in user_doc and user_doc[k] is not None for k in ["age", "height_cm", "weight_kg", "gender", "lifestyle", "goal"]):
            calorie_target = calculate_tdee(
                age=int(user_doc["age"]),
                height_cm=float(user_doc["height_cm"]),
                weight_kg=float(user_doc["weight_kg"]),
                gender=user_doc["gender"],
                lifestyle=user_doc["lifestyle"],
                goal=user_doc["goal"],
            )
            weight_kg = float(user_doc["weight_kg"])
            # Protein: 1.6g per kg of body weight
            protein_target = round(weight_kg * 1.6, 1)
            # Water: 35ml per kg of body weight, min 2000ml, max 4000ml
            water_target = max(2000, min(4000, round(weight_kg * 35)))

            return GoalTargets(
                calorie_target=calorie_target,
                protein_target_g=protein_target,
                water_target_ml=water_target
            )
    except Exception as e:
        logger.error("Failed to load user profile targets, using defaults", error=str(e))

    # Defaults
    return GoalTargets(
        calorie_target=2000,
        protein_target_g=80.0,
        water_target_ml=2500
    )


def get_weekly_dashboard(user_id: str, week_start: date) -> DashboardResponse:
    """
    Compile the full weekly dashboard for a user.

    Args:
        user_id:    The user's UUID.
        week_start: ISO date for the Monday of the target week.

    Returns:
        DashboardResponse with daily entries, summary statistics, and chart series.
    """
    week_end = week_start + timedelta(days=6)
    db_entries = _get_weekly_entries(user_id, week_start)
    summary = _compute_summary(db_entries)

    # Pad entries to exactly 7 days
    padded_entries: List[DailyEntry] = []
    db_entries_by_date = {e.date: e for e in db_entries}
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        if current_date in db_entries_by_date:
            padded_entries.append(db_entries_by_date[current_date])
        else:
            padded_entries.append(
                DailyEntry(
                    date=current_date,
                    calories_consumed=0,
                    protein_g=0.0,
                    water_ml=0,
                    weight_kg=None,
                    meals=[],
                    feedback_rating=None,
                    feedback_comment=None,
                )
            )

    charts = _build_charts_data(padded_entries)
    goals = get_user_goals(user_id)

    logger.info(
        "Dashboard compiled",
        user_id=user_id,
        week_start=week_start.isoformat(),
        days_with_data=len(db_entries),
    )

    return DashboardResponse(
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        daily_entries=padded_entries,
        summary=summary,
        charts_data=charts,
        goals=goals,
    )

