"""
Camada de conexão com o banco de dados (SQLAlchemy 2.x).

Aqui criamos três peças que o projeto inteiro reutiliza:
  - engine       : o "motor" que fala com o MySQL.
  - SessionLocal : uma fábrica de sessões (cada requisição usa uma).
  - Base         : a classe-mãe de todos os modelos (tabelas como classes).

E a dependência `get_db`, que entrega uma sessão para cada rota e garante
que ela seja fechada ao final — mesmo que ocorra um erro.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# O "motor" de conexão. pool_pre_ping evita usar conexões que caíram.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DB_ECHO,
)

# Fábrica de sessões. Uma sessão = uma "conversa" com o banco.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Classe-base dos modelos. A partir do tutorial 05, cada tabela vira
# uma classe que herda desta Base.
Base = declarative_base()


def get_db():
    """
    Dependência do FastAPI: abre uma sessão, entrega para a rota e fecha
    no final. Use com Depends(get_db) nas rotas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
