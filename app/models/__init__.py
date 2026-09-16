"""
Reúne os modelos para que o SQLAlchemy os registre ao importar o pacote.
"""
from app.models.permissao import Permissao
from app.models.perfil import Perfil
from app.models.usuario import Usuario

__all__ = ["Usuario", "Perfil", "Permissao"]
