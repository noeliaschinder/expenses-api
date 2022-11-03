from enum import Enum


class PeriodoAplicacionConsumo(Enum):
    PROXIMO_MES = 'proximo_mes'
    SIGUIENTE_MES = 'siguiente_mes'
    ACTUAL = 'actual'
