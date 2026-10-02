from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import requer_permissao
from app.database import get_db
from app.repositories import curso as repo
from app.schemas.common import Page
from app.schemas.curso import CursoCreate, CursoOut, CursoUpdate

router = APIRouter(prefix="/curso", tags=["Curso"])

# A mesma permissão para todas as rotas: declaramos uma vez.
_permissao = Depends(requer_permissao("curso.gerenciar"))

@router.get("", response_model=Page[CursoOut])
def listar(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1,le=100),
            incluir_inativos: bool = False,
            db: Session = Depends(get_db), _=_permissao):
    total, itens = repo.listar(db, offset, limit, incluir_inativos)
    return Page[CursoOut](total=total, limit=limit, offset=offset, items=itens)

@router.get("/{id_curso}", response_model=CursoOut)
def detalhar(id_curso: int, db: Session = Depends(get_db), _=_permissao):
    curso = repo.obter(db, id_curso)
    if curso is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso não encontrado")
    return curso

@router.post("", response_model=CursoOut, status_code=status.HTTP_201_CREATED)
def criar(dados: CursoCreate, db: Session = Depends(get_db), _=_permissao):
    return repo.criar(db, dados)

@router.put("/{id_curso}", response_model=CursoOut)
def atualizar(id_curso: int, dados:CursoUpdate,
        db: Session = Depends(get_db), _=_permissao):
    curso = repo.obter(db, id_curso)
    if curso is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso não encontrado")
    return repo.atualizar(db, curso, dados)

@router.delete("/{id_curso}", status_code=status.HTTP_204_NO_CONTENT)
def remover(id_curso: int, db: Session = Depends(get_db), _=_permissao):
    curso = repo.obter(db, id_curso)
    if curso is None:
        raise HTTPException(status.HHTTP_404_NOT_FOUND, "Curso não encontrado")
    repo.remover(db, curso)