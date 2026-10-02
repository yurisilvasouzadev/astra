from pydantic import BaseModel, ConfigDict, Field

class CursoBase(BaseModel):
    nome_curso: str = Field(min_length=2, max_length=120)
    desc_curso: str | None = None
    ch_curso: int | None = Field(default=None, ge=0)
    sigla_curso: str | None = Field(default=None, max_length=15)

class CursoCreate(CursoBase):
    pass

class CursoUpdate(BaseModel):               # tudo opcional -> edição parcial
    nome_curso: str | None = Field(default=None, min_length=2, max_length=120)
    desc_curso: str | None = None
    ch_curso: int | None = Field(default=None, ge=0)
    sigla_curso: str | None = Field(default=None, max_length=15)
    ativo: bool | None = None

class CursoOut(CursoBase):
    model_config = ConfigDict(from_attributes=True)   # cria a partir do objeto ORM
    id_curso: int
    ativo: bool