from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.disciplina import Disciplina
from app.schemas.disciplina import DisciplinaCreate, DisciplinaUpdate

def listar(
    db: Session,
    offset: int = 0, 
    limit: int = 20,
    id_curso: int | None = None, 
    incluir_inativos: bool = False,
) -> tuple[int, list[Disciplina]]:
    """Lista disciplinas, com filtro opcional por curso."""
    stmt = select(Disciplina)
    cnt = select(func.count(Disciplina.id_disc))
    if not incluir_inativos:
        stmt = stmt.where(Disciplina.ativo.is_(True))
        cnt = cnt.where(Disciplina.ativo.is_(True))
    if id_curso is not None:
        stmt = stmt.where(Disciplina.id_curso == id_curso)
        cnt = cnt.where(Disciplina.id_curso == id_curso)
    
    total = db.scalar(cnt) or 0
    itens = db.scalars(
        stmt.order_by(Disciplina.etapa, Disciplina.nome_disc)
        .offset(offset)
        .limit(limit)
    ).all()
    return total, list(itens)

def obter(db: Session, id_disc: int) -> Disciplina | None:
    return db.get(Disciplina, id_disc)

def criar(db: Session, dados: DisciplinaCreate) -> Disciplina:
    disciplina = Disciplina(**dados.model_dump())
    db.add(disciplina)
    db.commit()
    db.refresh(disciplina)
    return disciplina

def atualizar(
    db: Session, disciplina: Disciplina, dados: DisciplinaUpdate
) -> Disciplina:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(disciplina, campo, valor)
    db.commit()
    db.refresh(disciplina)
    return disciplina

def remover(db: Session, disciplina: Disciplina) -> None:
    disciplina.ativo = False
    db.commit()