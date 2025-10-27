from sqlalchemy import String, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base

class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    capital: Mapped[str | None] = mapped_column(String, nullable=True)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_code: Mapped[str | None] = mapped_column(String, nullable=True)
    exchange_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_gdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    flag_url: Mapped[str | None] = mapped_column(String, nullable=True)
    last_refreshed_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
