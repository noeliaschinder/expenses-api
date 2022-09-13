from enum import Enum


class PeriodoAplicacionConsumo(Enum):
    PROXIMO_MES = 'proximo mes (actual + 1)'
    SIGUIENTE_MES = 'otro mes (actual + 2)'
    ACTUAL = 'actual'
