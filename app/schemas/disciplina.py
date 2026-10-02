from pydantic import BaseModel, ConfigDict, Field

class DisciplinaBase(BaseModel):
    nome_disc: str = Field(min_length=2, max_length=120)
    sigla_disc: str | None = Field(default=None, max_length=15)
    ch_disc: int | None = Field(default=None, ge=0)
    etapa: int = Field(ge=1, le=3)
    id_curso: int

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaUpdate(BaseModel):               # tudo opcional -> edição parcial
    nome_disc: str | None = Field(default=None, min_length=2, max_length=120)
    sigla_disc: str | None = Field(default=None, max_length=15)
    ch_disc: int | None = Field(default=None, ge=0)
    etapa: int | None = Field(default=None, ge=1, le=3)
    id_curso: int | None = None
    ativo: bool | None = None

class DisciplinaOut(DisciplinaBase):
    model_config = ConfigDict(from_attributes=True)   # cria a partir do objeto ORM
    
    id_disc: int
    ativo: bool