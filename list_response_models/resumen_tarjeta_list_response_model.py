from sqlmodel import SQLModel

from schemas import GastoTarjetaOutput, DebitoAutomaticoOutput


class ResumenTarjetaListResponseModel(SQLModel):
    consumos: list[GastoTarjetaOutput]
    debitos_automaticos: list[DebitoAutomaticoOutput]
    summary: dict
