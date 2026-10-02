from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.curso import Curso
from app.schemas.curso import CursoCreate, CursoUpdate

def listar(
        db: Session, 
        offset: int = 0, 
        limit: int = 20, 
        incluir_inativos: bool = False
) -> tuple[int. list[Curso]]:
    """Retorna (total, itens). Por padrão, só curso ativos."""
    stmt = select(Curso)
    cnt = select(func.count(Curso.id_curso))
    if not incluir_inativos:
        stmt = stmt.where(Curso.ativo.is_(True))
        cnt = cnt.where(Curso.ativo.is_(True))
    total = db.scalar(cnt) or 0
    itens = db.scalars(stmt.order_by(Curso.nome_curso).offset(offset).limit(limit)).all()
    return total, list(itens)

def obter(db, id_curso):
    return db.get(Curso, id_curso)

def criar(db, dados: CursoCreate):
    curso = Curso(**dados.model_dump())
    db.add(curso); db.commit(); db.refresh(curso)
    return curso

def atualizar(db, curso, dados: CursoUpdate):
    # exclude_unset: só altera o que o cliente realmente enviou
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(curso, campo, valor)
    db.commit(); db.refresh(curso)
    return curso

def remover(db, curso):
    curso.ativo = False  # Soft DELETE: não apaga a linha
    db.commit()