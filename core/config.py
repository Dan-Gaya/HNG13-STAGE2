import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    EXTERNAL_COUNTRY_API = os.getenv("EXTERNAL_COUNTRY_API")
    EXTERNAL_EXCHANGE_API = os.getenv("EXTERNAL_EXCHANGE_API")
    PORT = int(os.getenv("PORT", 8000))
settings = Settings()

# class Settings:
#     DATABASE_URL="postgresql+asyncpg://postgres:abba1234@db.blpsygeggyzfywaudaix.supabase.co:5432/postgres"
#     EXTERNAL_COUNTRY_API="https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
#     EXTERNAL_EXCHANGE_API="https://open.er-api.com/v6/latest/USD"
#     PORT=8000

# settings = Settings()





