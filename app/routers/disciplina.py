from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import requer_permissao
from app.database import get_db
from app.repositories import curso as curso_repo
from app.repositories import disciplina as repo
from app.schemas.common import Page
from app.schemas.disciplina import DisciplinaCreate, DisciplinaOut, DisciplinaUpdate

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])

# A mesma permissão para todas as rotas: declaramos uma vez.
_permissao = Depends(requer_permissao("disciplina.gerenciar"))

def _validar_curso(db, id_curso: int) -> None:
    """garante que a disciplina referenciado existe (evita FK órfã)."""
    if curso_repo.obter(db, id_curso) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Curso {id_curso} não existe")

@router.get("", response_model=Page[DisciplinaOut])
def listar(
    offset: int = Query(0, ge=0), 
    limit: int = Query(20, ge=1, le=100),
    id_curso: int | None = None,
    incluir_inativos: bool = False,
    db: Session = Depends(get_db), 
    _=_permissao,
):
    total, itens = repo.listar(db, offset, limit, id_curso, incluir_inativos)
    return Page[DisciplinaOut](total=total, limit=limit, offset=offset, items=itens)

@router.get("/{id_disc}", response_model=DisciplinaOut)
def detalhar(id_disc: int, db: Session = Depends(get_db), _=_permissao):
    disciplina = repo.obter(db, id_disc)
    if disciplina is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Disciplina não encontrada")
    return disciplina

@router.post("", response_model=DisciplinaOut, status_code=status.HTTP_201_CREATED)
def criar(dados: DisciplinaCreate, db: Session = Depends(get_db), _=_permissao):
    _validar_curso(db, dados.id_curso)     # <- a checagem extra
    return repo.criar(db, dados)

@router.put("/{id_disc}", response_model=DisciplinaOut)
def atualizar(
    id_disc: int, 
    dados:DisciplinaUpdate,
    db: Session = Depends(get_db), 
    _=_permissao,
):
    disciplina = repo.obter(db, id_disc)
    if disciplina is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Discipina não encontrada")
    if dados.id_curso is not None:
        _validar_curso(db, dados.id_curso)
    return repo.atualizar(db, disciplina, dados)

@router.delete("/{id_disc}", status_code=status.HTTP_204_NO_CONTENT)
def remover(id_disc: int, db: Session = Depends(get_db), _=_permissao):
    disciplina = repo.obter(db, id_disc)
    if disciplina is None:
        raise HTTPException(status.HHTTP_404_NOT_FOUND, "Disciplina não encontrada")
    repo.remover(db, disciplina)