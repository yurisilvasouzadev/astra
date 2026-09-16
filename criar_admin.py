"""
Cria o usuário administrador inicial do ASTRA.

Como o script.sql cadastra os perfis e permissões, mas nenhum usuário,
este utilitário cria o primeiro Admin — com a senha já em hash — para
você conseguir fazer login. Depois, mude a senha no primeiro acesso.

Uso (com o .venv ativo e o banco no ar):
    python criar_admin.py
"""
from sqlalchemy import select

from app.core.security import hash_senha
from app.database import SessionLocal
from app.models.perfil import Perfil
from app.models.usuario import Usuario

EMAIL = "admin@astra.local"
SENHA = "admin123"          # provisória — troque no primeiro acesso
NOME = "Administrador"


def main() -> None:
    db = SessionLocal()
    try:
        perfil_admin = db.scalar(
            select(Perfil).where(Perfil.nome_perfil == "Admin")
        )
        if perfil_admin is None:
            print("Perfil 'Admin' não encontrado. Rode o script.sql primeiro.")
            return

        ja_existe = db.scalar(
            select(Usuario).where(Usuario.email_usu == EMAIL)
        )
        if ja_existe is not None:
            print(f"Usuário já existe: {EMAIL}")
            return

        admin = Usuario(
            nome_usu=NOME,
            email_usu=EMAIL,
            senha_usu=hash_senha(SENHA),
            senha_provisoria=True,
            status_usu="ATIVO",
        )
        admin.perfis.append(perfil_admin)
        db.add(admin)
        db.commit()
        print(f"Admin criado: {EMAIL} / {SENHA}  (troque no primeiro acesso)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
