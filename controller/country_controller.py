from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from schemas.country_schema import CountryResponse
from models.country_model import Country
from services.country_service import fetch_and_refresh_countries
from services.image_service import SUMMARY_IMG, generate_summary_image
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import os

router = APIRouter(prefix="/countries", tags=["Countries"])


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_IMG = os.path.join(BASE_DIR, "..", "cache", "summary.png")


@router.get("/image")
def get_summary_image():
    if not os.path.exists(SUMMARY_IMG):
        return {"error": "Summary image not found"}
    return FileResponse(SUMMARY_IMG, media_type="image/png")

@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_db)):
    """
    Returns total number of countries and the last refresh timestamp (ISO8601 UTC with 'Z').
    """
    try:
        # Count countries
        total_result = await db.execute(select(func.count()).select_from(Country))
        total = total_result.scalar() or 0

        # Latest refresh timestamp
        latest_result = await db.execute(select(func.max(Country.last_refreshed_at)))
        latest = latest_result.scalar()

        # Normalize and format datetime
        if latest:
            if latest.tzinfo is not None:
                latest = latest.astimezone(timezone.utc).replace(tzinfo=None)
            latest = latest.isoformat(timespec="seconds") + "Z"

        return {
            "total_countries": total,
            "last_refreshed_at": latest or None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"Failed to fetch status: {str(e)}"})

# 🔹 GET ALL COUNTRIES (filter + sort)
@router.get("/", response_model=list[CountryResponse])
async def get_countries(
    region: str | None = Query(None),
    currency: str | None = Query(None),
    sort: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Country)

    if region:
        stmt = stmt.where(Country.region.ilike(region))
    if currency:
        stmt = stmt.where(Country.currency_code.ilike(currency))
    if sort == "gdp_desc":
        stmt = stmt.order_by(Country.estimated_gdp.desc())

    result = await db.execute(stmt)
    countries = result.scalars().all()
    return countries

# 🔹 REFRESH COUNTRY DATA
@router.post("/refresh")
async def refresh_countries(db: AsyncSession = Depends(get_db)):
    result = await fetch_and_refresh_countries(db)
    if isinstance(result, tuple):
        content, status = result
        raise HTTPException(status_code=status, detail=content)
    return result


# 🔹 GET A SINGLE COUNTRY BY NAME
@router.get("/{name}", response_model=CountryResponse)
async def get_country(name: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Country).where(Country.name.ilike(name))
    result = await db.execute(stmt)
    country = result.scalar_one_or_none()

    if not country:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    return country


# 🔹 DELETE COUNTRY BY NAME
@router.delete("/{name}")
async def delete_country(name: str, db: AsyncSession = Depends(get_db)):
    # Check existence first
    stmt = select(Country).where(Country.name.ilike(name))
    result = await db.execute(stmt)
    country = result.scalar_one_or_none()

    if not country:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})

    await db.delete(country)
    await db.commit()

    return {"message": f"{name} deleted successfully"}
