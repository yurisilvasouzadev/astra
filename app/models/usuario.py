"""
Modelo Usuario — a conta de acesso.
Um usuário acumula perfis (N:N via usuario_perfil); a autorização é a
UNIÃO das permissões de todos os seus perfis.
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.associations import usuario_perfil
from app.models.perfil import Perfil


class Usuario(Base):
    __tablename__ = "usuario"

    id_usu: Mapped[int] = mapped_column(primary_key=True)
    nome_usu: Mapped[str]
    email_usu: Mapped[str]
    senha_usu: Mapped[str]                      # guarda o HASH, nunca a senha
    senha_provisoria: Mapped[bool] = mapped_column(default=True)
    status_usu: Mapped[str] = mapped_column(default="ATIVO")

    # Os perfis deste usuário (Admin, Professor, Coordenador...).
    perfis: Mapped[list[Perfil]] = relationship(
        secondary=usuario_perfil,
        lazy="selectin",
    )
