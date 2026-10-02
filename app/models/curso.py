from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Curso(Base):
    __tablename__= "curso"
    id_curso: Mapped[int] = mapped_column(primary_key=True)
    nome_curso: Mapped[str]
    desc_curso: Mapped[str] = mapped_column(nullable=True, default=None)
    ch_curso: Mapped[int] = mapped_column(nullable=True, default=None)
    sigla_curso: Mapped[str] = mapped_column(nullable=True, default=None)
    ativo: Mapped[bool] = mapped_column(default=True)   #soft delete