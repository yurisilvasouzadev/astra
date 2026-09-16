"""
Dependências de autenticação e autorização.

- get_current_user: descobre QUEM está chamando (a partir do token).
- permissoes_do_usuario: calcula a UNIÃO das permissões dos perfis.
- requer_permissao: fábrica de dependências que exige permissões numa rota.

Uso típico numa rota protegida:

    @router.post("/alunos")
    def criar(usuario = Depends(requer_permissao("aluno.criar")), ...):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_token
from app.database import get_db
from app.models.usuario import Usuario

# Diz ao FastAPI onde se obtém o token (usado também pelo botão "Authorize").
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida o token e devolve o usuário correspondente."""
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decodificar_token(token)
    if payload is None or "sub" not in payload:
        raise credenciais_invalidas

    usuario = db.get(Usuario, int(payload["sub"]))
    if usuario is None or usuario.status_usu != "ATIVO":
        raise credenciais_invalidas
    return usuario


def permissoes_do_usuario(usuario: Usuario) -> set[str]:
    """Todas as permissões do usuário = união das permissões de seus perfis."""
    return {
        permissao.chave_permissao
        for perfil in usuario.perfis
        for permissao in perfil.permissoes
    }


def requer_permissao(*chaves: str):
    """
    Cria uma dependência que só deixa passar quem tem TODAS as permissões
    informadas. É a checagem central do RBAC.
    """
    def verificador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        do_usuario = permissoes_do_usuario(usuario)
        if not set(chaves).issubset(do_usuario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta ação",
            )
        return usuario

    return verificador
