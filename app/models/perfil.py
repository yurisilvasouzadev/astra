"""
Modelo Perfil — um papel de acesso (Admin, Secretaria, Professor...).
Cada perfil concede um conjunto de permissões (N:N via perfil_permissao).
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.associations import perfil_permissao
from app.models.permissao import Permissao


class Perfil(Base):
    __tablename__ = "perfil"

    id_perfil: Mapped[int] = mapped_column(primary_key=True)
    nome_perfil: Mapped[str]
    # descricao: Mapped[str | None] = mapped_column(default=None)
    descricao: Mapped[str] = mapped_column(nullable=True, default=None)
    ativo: Mapped[bool] = mapped_column(default=True)

    # As permissões deste perfil. selectin já carrega junto, evitando N+1.
    permissoes: Mapped[list[Permissao]] = relationship(
        secondary=perfil_permissao,
        lazy="selectin",
    )
