"""
Modelo Permissao — uma ação atômica autorizável (ex.: 'aluno.criar').
Mapeia a tabela `permissao` já criada pelo script.sql.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Permissao(Base):
    __tablename__ = "permissao"

    id_permissao: Mapped[int] = mapped_column(primary_key=True)
    chave_permissao: Mapped[str]
    # descricao: Mapped[str | None] = mapped_column(default=None)
    descricao: Mapped[str] = mapped_column(nullable=True, default=None)
