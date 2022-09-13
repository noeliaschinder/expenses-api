from decimal import Decimal

from sqlmodel import Session

from schemas import Balance, BalanceMovimiento
from helpers.ingresos_helper import IngresosHelper
from helpers.egresos_helper import EgresosHelper


class BalancesHelper():

    @classmethod
    def generar_balance(cls, periodo: str, session: Session, balance: Balance = None):
        if balance == None:
            balance = Balance(periodo=periodo)
            balance.periodo = periodo
        else:
            movimientos = balance.movimientos
            for movimiento in movimientos:
                session.delete(movimiento)
            session.commit()

        session.add(balance)
        session.commit()
        session.refresh(balance)

        grupos_ingresos = IngresosHelper.get_ingresos_para_periodo(periodo, session)
        total_ingresos = 0
        for tipo_ingreso in grupos_ingresos:
            ingresos = grupos_ingresos[tipo_ingreso]
            if ingresos:
                for ingreso in ingresos:
                    total_ingresos += Decimal(ingreso['importe'])
                    movimiento_ingreso = BalanceMovimiento(importe=ingreso['importe'],
                                                           concepto=ingreso['concepto'], tipo="ingreso",
                                                           balance_id=balance.id, entity_id=ingreso['entity_id'],
                                                           entity=tipo_ingreso)
                    session.add(movimiento_ingreso)

        grupos_egresos = EgresosHelper.get_gastos_para_periodo(periodo, session)
        total_egresos = 0
        for tipo_egreso in grupos_egresos:
            egresos = grupos_egresos[tipo_egreso]
            if egresos:
                for egreso in egresos:
                    total_egresos += Decimal(egreso['importe'])
                    movimiento_egreso = BalanceMovimiento(importe=egreso['importe'],
                                                          concepto=egreso['concepto'], tipo="egreso",
                                                          balance_id=balance.id, entity_id=egreso['entity_id'],
                                                          entity=tipo_egreso, categoria_id=egreso['categoria_id'])
                    session.add(movimiento_egreso)

        balance.importe_total_egresos = total_egresos
        balance.importe_saldo = total_ingresos - total_egresos
        balance.importe_total_ingresos = total_ingresos
        session.commit()
        session.refresh(balance)

    @classmethod
    def get_saldo(cls, movimientos):
        sum = 0
        for movimiento in movimientos:
            if movimiento.tipo == 'ingreso':
                sum = sum + movimiento.importe
            else:
                sum = sum - movimiento.importe
        return sum