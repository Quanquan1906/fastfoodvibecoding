"""Debug startup script to test backend initialization"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 50)
print("🔍 FastFood Backend - Debug Start")
print("=" * 50)

# Check environment variables
print("\n📋 Environment Variables:")
print(f"  MONGODB_URL: {os.getenv('MONGODB_URL', 'NOT SET')}")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")

# Test database connection
print("\n🔗 Testing MongoDB Connection...")
try:
    from app.core.database import connect_db, close_db
    
    async def test_connection():
        try:
            await connect_db()
            print("  ✅ MongoDB connection successful!")
            await close_db()
            return True
        except Exception as e:
            print(f"  ❌ MongoDB connection failed: {e}")
            return False
    
    result = asyncio.run(test_connection())
    if not result:
        print("\n⚠️  MongoDB connection failed. Check:")
        print("  1. Is MongoDB Atlas reachable?")
        print("  2. Are credentials correct in .env file?")
        print("  3. Is your IP whitelisted in MongoDB Atlas?")
        exit(1)
        
except Exception as e:
    print(f"  ❌ Error testing connection: {e}")
    exit(1)

# Test FastAPI app creation
print("\n🚀 Testing FastAPI App Creation...")
try:
    from backend.main import app
    print("  ✅ FastAPI app created successfully!")
except Exception as e:
    print(f"  ❌ Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 50)
print("✅ All checks passed! Starting server...\n")
print("=" * 50)

# Start the server
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
