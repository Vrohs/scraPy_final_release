import asyncio
import hashlib
import secrets
from app.core.database import AsyncSessionLocal
from app.models.api_key import ApiKey

async def create_test_key():
    # Generate a raw key
    raw_key = f"sk_test_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:8]
    
    async with AsyncSessionLocal() as session:
        new_key = ApiKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id="user_test_123",
            name="Test Key",
            is_active=True,
            rate_limit=100
        )
        session.add(new_key)
        await session.commit()
        print(f"Created API Key: {raw_key}")

if __name__ == "__main__":
    asyncio.run(create_test_key())
