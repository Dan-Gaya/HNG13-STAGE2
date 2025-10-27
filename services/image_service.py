import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.country_model import Country


# ✅ Use project root instead of module directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # go one level up
CACHE_DIR = os.path.join(BASE_DIR, "cache")
SUMMARY_IMG = os.path.join(CACHE_DIR, "summary.png")

# CACHE_DIR = "cache"
# SUMMARY_IMG = os.path.join(CACHE_DIR, "summary.png")


async def generate_summary_image(db: AsyncSession, last_refreshed_at: datetime):
    os.makedirs(CACHE_DIR, exist_ok=True)

    # ✅ Get total countries (async)
    total_result = await db.execute(select(func.count()).select_from(Country))
    total_countries = total_result.scalar() or 0

    # ✅ Get top 5 countries by GDP (async)
    top_result = await db.execute(
        select(Country)
        .where(Country.estimated_gdp.isnot(None))
        .order_by(Country.estimated_gdp.desc())
        .limit(5)
    )
    top_countries = top_result.scalars().all()

    # 🎨 Create image
    width, height = 800, 400
    img = Image.new("RGB", (width, height), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)

    # 🧩 Font setup
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_text = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # 📝 Title
    draw.text((20, 20), "🌍 Country Currency & Exchange Summary", font=font_title, fill=(0, 0, 0))

    # 🕒 Stats
    draw.text((20, 70), f"Total Countries: {total_countries}", font=font_text, fill=(0, 0, 80))
    draw.text(
        (20, 100),
        f"Last Refreshed: {last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        font=font_text,
        fill=(0, 0, 80),
    )

    # 💰 Top 5 by GDP
    y = 150
    draw.text((20, y - 30), "Top 5 Countries by Estimated GDP:", font=font_text, fill=(20, 20, 20))
    for i, c in enumerate(top_countries, start=1):
        draw.text((40, y), f"{i}. {c.name} — GDP: {c.estimated_gdp:,.2f}", font=font_text, fill=(50, 50, 50))
        y += 30

    # 💾 Save image
    img.save(SUMMARY_IMG)
    return SUMMARY_IMG
