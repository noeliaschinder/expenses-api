from sqlmodel import SQLModel

from schemas import TarjetaOutput


class TarjetaListResponseModel(SQLModel):
    data: list[TarjetaOutput]
    count: int
    summary: dict
