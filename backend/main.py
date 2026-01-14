"""FastAPI main application for FastFood delivery system"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.persistence.database import connect_db, close_db
from app.presentation.routers import auth_router, restaurant_router, order_router, menu_item_router, drone_router, user_router, health_router
from app.presentation.websocket.ws_router import router as ws_router

# Create FastAPI app
app = FastAPI(
    title="FastFood Delivery API",
    description="Demo drone food delivery system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Dev-friendly CORS: allow React dev server and any localhost/127.0.0.1 origin.
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(restaurant_router.router)
app.include_router(order_router.router)
app.include_router(menu_item_router.router)
app.include_router(drone_router.router)
app.include_router(user_router.router)
app.include_router(health_router.router)
app.include_router(ws_router)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_db()
    print("🚀 FastFood API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_db()
    print("🛑 FastFood API stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
