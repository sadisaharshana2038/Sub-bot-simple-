#!/usr/bin/env python3
"""
Database Setup Script
Initialize MongoDB collections and indexes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def setup():
    """Setup database"""
    
    print("\n" + "="*50)
    print("🗄️  DATABASE SETUP")
    print("="*50 + "\n")
    
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('DB_NAME', 'sinhala_sub_bot')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not set!")
        return
    
    print("📡 Connecting...")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    try:
        await client.admin.command('ping')
        print(f"✅ Connected to: {db_name}\n")
        
        # Create indexes
        print("📊 Creating indexes...")
        
        await db.users.create_index("user_id", unique=True)
        print("  ✅ Users")
        
        await db.series.create_index("series_id", unique=True)
        await db.series.create_index([("title_en", "text"), ("title_si", "text")])
        print("  ✅ Series")
        
        await db.episodes.create_index("episode_id", unique=True)
        await db.episodes.create_index("series_id")
        print("  ✅ Episodes")
        
        await db.downloads.create_index("user_id")
        print("  ✅ Downloads")
        
        print("\n" + "="*50)
        print("✅ SETUP COMPLETE!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(setup())
