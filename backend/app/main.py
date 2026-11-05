from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SHY BOUTIQUE API",
    version="0.1.0",
    description="API e-commerce de SHY BOUTIQUE",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "shy-boutique-api"}


@app.get("/api/v1", tags=["meta"])
def api_root() -> dict[str, str]:
    return {"name": "SHY BOUTIQUE API", "version": "0.1.0"}
