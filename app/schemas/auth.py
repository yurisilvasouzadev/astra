"""
Schemas Pydantic da autenticação: moldam o que entra e o que sai da API.
"""
from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """Resposta do login."""
    access_token: str
    token_type: str = "bearer"
    senha_provisoria: bool  # True => o front deve forçar a troca de senha


class TrocaSenha(BaseModel):
    """Entrada da troca de senha (perfil do usuário / primeiro acesso)."""
    senha_atual: str
    senha_nova: str = Field(min_length=6)


class UsuarioOut(BaseModel):
    """Dados públicos do usuário (nunca inclui a senha)."""
    model_config = ConfigDict(from_attributes=True)

    id_usu: int
    nome_usu: str
    email_usu: str
    status_usu: str
    senha_provisoria: bool
