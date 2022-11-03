from sqlmodel import SQLModel

from schemas import GastoTarjetaOutput


class GastoTarjetaListResponseModel(SQLModel):
    data: list[GastoTarjetaOutput]
    count: int
    summary: dict
