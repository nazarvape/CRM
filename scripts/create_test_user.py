#!/usr/bin/env python3
"""
Script to create test user and migrate existing clients
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

# Load environment
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    """Create test user and migrate existing clients"""
    
    # Create test user
    test_user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash("password123")
    
    user_data = {
        "id": test_user_id,
        "email": "test@example.com",
        "full_name": "Тестовий Користувач",
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": "test@example.com"})
    if not existing_user:
        await db.users.insert_one(user_data)
        print("✅ Test user created - test@example.com / password123")
    else:
        test_user_id = existing_user["id"]
        print("✅ Test user already exists - test@example.com / password123")
    
    # Migrate existing clients to test user
    result = await db.clients.update_many(
        {"user_id": {"$exists": False}},
        {"$set": {"user_id": test_user_id}}
    )
    
    print(f"✅ Migrated {result.modified_count} clients to test user")
    
    return test_user_id

async def main():
    """Main function"""
    print("Creating test user and migrating clients...")
    
    try:
        await create_test_user()
        print("Setup completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())