from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CountryBase(BaseModel):
    id: int
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: datetime


class CountryResponse(CountryBase):
    class Config:
        orm_mode = True
