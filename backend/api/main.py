from fastapi import FastAPI
from api.endpoints.solar_flare import router as solar_flare_router
from api.endpoints.analysis import router as analysis_router

app = FastAPI()

# Solar Flare routes
app.include_router(solar_flare_router, prefix="/api")

# analysis routes
app.include_router(analysis_router, prefix="/api/analysis")