from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Disciplina(Base):
    __tablename__ = "disciplina"
    id_disc: Mapped[int] = mapped_column(primary_key=True)
    nome_disc: Mapped[str]
    sigla_disc: Mapped[str] = mapped_column(nullable=True, default=None)
    ch_disc: Mapped[int] = mapped_column(nullable=True, default=None)
    etapa: Mapped[int]                                   # 1, 2 ou 3
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))
    ativo: Mapped[bool] = mapped_column(default=True)