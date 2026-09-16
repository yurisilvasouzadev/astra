"""
Funções de segurança do ASTRA: hash de senha e tokens JWT.

- Senhas nunca são guardadas em texto puro: gravamos o HASH (bcrypt).
- O login devolve um token JWT assinado com a SECRET_KEY; cada requisição
  seguinte apresenta esse token para provar quem é.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

# O bcrypt aceita no máximo 72 bytes; truncamos por segurança.
_MAX_BYTES = 72


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto."""
    senha_bytes = senha.encode("utf-8")[:_MAX_BYTES]
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere se a senha informada corresponde ao hash guardado."""
    senha_bytes = senha.encode("utf-8")[:_MAX_BYTES]
    return bcrypt.checkpw(senha_bytes, hash_armazenado.encode("utf-8"))


def criar_access_token(sub: str | int) -> str:
    """Cria um JWT cujo 'sub' (subject) é o id do usuário."""
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(sub), "exp": expira}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict | None:
    """Valida e decodifica o token. Retorna o payload ou None se inválido."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None
