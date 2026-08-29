from fastapi import FastAPI

from app.api.routes.sensors import router as sensors_router
from app.api.routes.drains import router as drains_router

app = FastAPI(
    title="FlowSentra API",
    description="Intelligent IoT-Based Drainage Monitoring and Risk Assessment System",
    version="1.0.0",
)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "message": "FlowSentra backend is running",
    }


app.include_router(sensors_router)
app.include_router(drains_router)