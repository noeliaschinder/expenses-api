from sqlmodel import SQLModel

from schemas import GastoCategoriaOutput


class GastoCategoriaListResponseModel(SQLModel):
    data: list[GastoCategoriaOutput]
    count: int
    summary: dict
