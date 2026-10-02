from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    total: int        # total de registros que atendem ao filtro
    limit: int        # tamanho da página
    offset: int       # a partir de qual registro
    items: list[T]    # os registros desta página