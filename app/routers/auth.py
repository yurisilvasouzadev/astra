"""
Rotas de autenticação do ASTRA.

  POST /auth/login            -> troca e-mail + senha por um token JWT
  GET  /auth/me               -> dados do usuário logado
  GET  /auth/minhas-permissoes-> lista as permissões efetivas
  POST /auth/trocar-senha     -> troca a própria senha (obrigatória no 1º acesso)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, permissoes_do_usuario
from app.core.security import criar_access_token, hash_senha, verificar_senha
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import Token, TrocaSenha, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # No fluxo OAuth2, o campo "username" carrega o e-mail.
    usuario = db.scalar(select(Usuario).where(Usuario.email_usu == form.username))
    if usuario is None or not verificar_senha(form.password, usuario.senha_usu):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    if usuario.status_usu != "ATIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário bloqueado ou inativo",
        )
    token = criar_access_token(sub=usuario.id_usu)
    return Token(access_token=token, senha_provisoria=usuario.senha_provisoria)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.get("/minhas-permissoes")
def minhas_permissoes(usuario: Usuario = Depends(get_current_user)):
    return sorted(permissoes_do_usuario(usuario))


@router.post("/trocar-senha")
def trocar_senha(
    dados: TrocaSenha,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verificar_senha(dados.senha_atual, usuario.senha_usu):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    usuario.senha_usu = hash_senha(dados.senha_nova)
    usuario.senha_provisoria = False
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}
