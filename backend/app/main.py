from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.sensors import router as sensors_router
from app.api.routes.drains import router as drains_router

app = FastAPI(
    title="FlowSentra API",
    description="Intelligent IoT-Based Drainage Monitoring and Risk Assessment System",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "message": "FlowSentra backend is running",
    }


app.include_router(sensors_router)
app.include_router(drains_router)