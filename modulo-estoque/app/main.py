from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import alertas, movimentacoes, produtos

app = FastAPI(
    title="Módulo Estoque — ERP Universitário",
    description="API REST para controle de estoque e almoxarifado",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(movimentacoes.router)
app.include_router(alertas.router)


@app.get("/health")
def health():
    return {"status": "ok", "modulo": "estoque"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8003, reload=True)
