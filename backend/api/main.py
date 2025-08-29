from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.endpoints.solar_flare import router as solar_flare_router
from api.endpoints.analysis import router as analysis_router

app = FastAPI()
# Exposes prometheus /metrics endpoint for grafana dashboard
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)  


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict before deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Solar Flare routes
app.include_router(solar_flare_router, prefix="/api")

# analysis routes
app.include_router(analysis_router, prefix="/api/analysis")