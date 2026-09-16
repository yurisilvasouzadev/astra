"""
Tabelas de associação (junção N:N) do controle de acesso.

Elas não viram classes — são apenas "pontes" entre outras tabelas.
Por isso as declaramos como Table, e não como classes que herdam de Base.
"""
from sqlalchemy import Column, ForeignKey, Table

from app.database import Base

# Quais perfis cada usuário acumula
usuario_perfil = Table(
    "usuario_perfil",
    Base.metadata,
    Column("id_usu", ForeignKey("usuario.id_usu"), primary_key=True),
    Column("id_perfil", ForeignKey("perfil.id_perfil"), primary_key=True),
)

# Quais permissões cada perfil concede
perfil_permissao = Table(
    "perfil_permissao",
    Base.metadata,
    Column("id_perfil", ForeignKey("perfil.id_perfil"), primary_key=True),
    Column("id_permissao", ForeignKey("permissao.id_permissao"), primary_key=True),
)
