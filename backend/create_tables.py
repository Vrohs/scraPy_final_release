import asyncio
from app.core.database import engine, Base
from app.models.job import Job
from app.models.api_key import ApiKey
from app.models.webhook import Webhook

async def create_tables():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
