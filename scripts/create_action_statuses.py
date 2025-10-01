#!/usr/bin/env python3
"""
Script to create default action status types
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

# Load environment
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def create_action_status_types():
    """Create default action status types"""
    action_status_types = [
        {
            "id": str(uuid.uuid4()),
            "name": "Зробив замовлення",
            "key": "made_order",
            "color": "#22C55E",  # зелений
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Пройшов опитування", 
            "key": "completed_survey",
            "color": "#8B5CF6",  # фіолетовий
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Сповістив про акцію",
            "key": "notified_about_promotion", 
            "color": "#8B5CF6",  # фіолетовий
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Має додаткові питання",
            "key": "has_additional_questions",
            "color": "#EF4444",  # червоний
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Передзвонити",
            "key": "need_callback", 
            "color": "#F59E0B",  # оранжевий
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Не виходить на зв'язок",
            "key": "not_answering",
            "color": "#EF4444",  # червоний
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Планує замовлення", 
            "key": "planning_order",
            "color": "#EAB308",  # жовтий
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Clear existing action status types
    await db.action_status_types.delete_many({})
    
    # Insert new action status types
    await db.action_status_types.insert_many(action_status_types)
    print(f"Created {len(action_status_types)} action status types")

async def main():
    """Main function"""
    print("Creating action status types...")
    
    try:
        await create_action_status_types()
        print("Action status types created successfully!")
    except Exception as e:
        print(f"Error creating action status types: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())