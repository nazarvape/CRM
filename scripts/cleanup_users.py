#!/usr/bin/env python3
"""
Script to cleanup duplicate users and help with login issues
"""
import asyncio
import sys
import os
from pathlib import Path
from collections import defaultdict

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import hashlib

# Load environment
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def cleanup_duplicate_users():
    """Remove duplicate users, keep the latest one"""
    
    print("🔍 Analyzing users...")
    users = await db.users.find().to_list(1000)
    
    # Group users by email
    email_groups = defaultdict(list)
    for user in users:
        email_groups[user['email']].append(user)
    
    print(f"Found {len(users)} total users with {len(email_groups)} unique emails")
    
    # Process duplicates
    for email, user_list in email_groups.items():
        if len(user_list) > 1:
            print(f"\n📧 Email: {email} has {len(user_list)} accounts")
            
            # Sort by creation date, keep the latest
            user_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            keep_user = user_list[0]
            remove_users = user_list[1:]
            
            print(f"  ✅ Keeping: {keep_user['full_name']} (ID: {keep_user['id']})")
            
            # Move clients from old users to the kept user
            for old_user in remove_users:
                print(f"  🔄 Moving clients from {old_user['full_name']} (ID: {old_user['id']})")
                
                # Update clients
                result = await db.clients.update_many(
                    {"user_id": old_user['id']},
                    {"$set": {"user_id": keep_user['id']}}
                )
                print(f"    Moved {result.modified_count} clients")
                
                # Delete old user
                await db.users.delete_one({"id": old_user['id']})
                print(f"  🗑️  Deleted duplicate user: {old_user['full_name']}")

async def reset_user_password(email, new_password="123456"):
    """Reset user password"""
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"hashed_password": password_hash}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Password reset for {email} to '{new_password}'")
    else:
        print(f"❌ User {email} not found")

async def main():
    """Main function"""
    print("🧹 User Cleanup Utility")
    print("=" * 50)
    
    try:
        # Cleanup duplicates
        await cleanup_duplicate_users()
        
        print("\n🔑 Resetting passwords for known users...")
        
        # Reset passwords for test users
        await reset_user_password("test@example.com", "123456")
        await reset_user_password("nazarvape@gmail.com", "123456")
        await reset_user_password("krossn1996@gmail.com", "123456")
        
        # Show final user list
        print("\n👥 Final user list:")
        users = await db.users.find().to_list(100)
        for user in users:
            clients_count = await db.clients.count_documents({"user_id": user['id']})
            print(f"  📧 {user['email']} - {user['full_name']} ({clients_count} клієнтів)")
        
        print(f"\n✅ Cleanup completed! You can now login with:")
        print(f"  Email: test@example.com")
        print(f"  Password: 123456")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())