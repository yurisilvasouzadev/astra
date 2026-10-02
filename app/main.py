"""
Ponto de entrada da API do ASTRA.

Sobe a aplicação FastAPI, registra os routers e expõe endpoints de status.

Rode com:  uvicorn app.main:app --reload
Docs em:   http://localhost:8000/docs
"""
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.routers import auth, curso, disciplina

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API do sistema de gestão escolar ASTRA.",
)

# Registro dos routers (um por área do sistema).
app.include_router(auth.router)
app.include_router(curso.router)
app.include_router(disciplina.router)


@app.get("/", tags=["Status"])
def raiz():
    """Confirma que a API está online."""
    return {
        "sistema": settings.APP_NAME,
        "versao": settings.APP_VERSION,
        "status": "online",
    }


@app.get("/health", tags=["Status"])
def health(db: Session = Depends(get_db)):
    """Verifica a saúde da API e a conexão com o banco de dados."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")
    return {"status": "ok", "banco": "conectado"}