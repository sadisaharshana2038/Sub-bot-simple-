"""
Database Test Script
Test MongoDB connection and check files
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'sinhala_sub_bot')

async def test_database():
    """Test database connection and show files"""
    print("🔄 Testing MongoDB connection...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URI)
        await client.admin.command('ping')
        db = client[DB_NAME]
        
        print("✅ Connected to MongoDB successfully!")
        print(f"📊 Database: {DB_NAME}")
        print()
        
        # Count documents
        users_count = await db.users.count_documents({})
        files_count = await db.files.count_documents({})
        searches_count = await db.searches.count_documents({})
        requests_count = await db.requests.count_documents({})
        banned_count = await db.banned_users.count_documents({})
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📈 Database Statistics:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"👥 Users: {users_count}")
        print(f"📁 Files: {files_count}")
        print(f"🔍 Searches: {searches_count}")
        print(f"📝 Requests: {requests_count}")
        print(f"🚫 Banned Users: {banned_count}")
        print()
        
        # Show sample files
        if files_count > 0:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("📁 Sample Files (first 5):")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            files = await db.files.find({}).limit(5).to_list(5)
            
            for idx, file in enumerate(files, 1):
                print(f"\n{idx}. {file.get('file_name', 'Unknown')}")
                print(f"   Type: {file.get('file_type', 'N/A')}")
                print(f"   Size: {file.get('file_size', 0)} bytes")
                print(f"   File ID: {file.get('file_id', 'N/A')[:20]}...")
        else:
            print("⚠️  No files found in database!")
            print("\n💡 To add files:")
            print("1. Add bot as admin to your channel")
            print("2. Post files to the channel")
            print("3. Files will be auto-indexed")
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ Database test completed!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Check your .env file:")
        print("- MONGODB_URI should be valid")
        print("- Database should be accessible")

if __name__ == '__main__':
    asyncio.run(test_database())
