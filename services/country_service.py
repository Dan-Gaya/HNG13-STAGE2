import random
import httpx
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.country_model import Country
from core.config import settings
from services.image_service import generate_summary_image


async def fetch_and_refresh_countries(db: AsyncSession):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            countries_resp = await client.get(settings.EXTERNAL_COUNTRY_API)
            rates_resp = await client.get(settings.EXTERNAL_EXCHANGE_API)

        if countries_resp.status_code != 200:
            return {
                "error": "External data source unavailable",
                "details": "Could not fetch data from Countries API"
            }, 503

        if rates_resp.status_code != 200:
            return {
                "error": "External data source unavailable",
                "details": "Could not fetch data from Exchange API"
            }, 503

        countries_data = countries_resp.json()
        rates = rates_resp.json().get("rates", {})

        now = datetime.utcnow()

        for c in countries_data:
            name = c.get("name")
            population = c.get("population")
            currencies = c.get("currencies", [])
            currency_code = currencies[0].get("code") if currencies else None
            exchange_rate = rates.get(currency_code)
            multiplier = random.randint(1000, 2000)

            estimated_gdp = None
            if exchange_rate and population:
                estimated_gdp = (population * multiplier) / exchange_rate

            # 🔄 Modern async ORM query
            result = await db.execute(
                select(Country).where(Country.name.ilike(name))
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.capital = c.get("capital")
                existing.region = c.get("region")
                existing.population = population
                existing.currency_code = currency_code
                existing.exchange_rate = exchange_rate
                existing.estimated_gdp = estimated_gdp
                existing.flag_url = c.get("flag")
                existing.last_refreshed_at = now
            else:
                db.add(Country(
                    name=name,
                    capital=c.get("capital"),
                    region=c.get("region"),
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=c.get("flag"),
                    last_refreshed_at=now
                ))

        await db.commit()        
        await generate_summary_image(db, now)
        print("Summary image generated successfully.")

    
        return {"message": "Data refreshed successfully", "last_refreshed_at": now}

    except httpx.RequestError as e:
        return {"error": "Network error", "details": str(e)}, 502

    except Exception as e:
        return {"error": "Internal server error", "details": str(e)}, 500
