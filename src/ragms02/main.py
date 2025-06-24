from fastapi import FastAPI
from ragms02.api.routes import router as base_router
from ragms02.api.ingest import router as ingest_router
from ragms02.api.query import router as query_router
from ragms02.api.admin import router as admin_router

app = FastAPI(title="RAGMS02 API")
app.include_router(base_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(admin_router)
