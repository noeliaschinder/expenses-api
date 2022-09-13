from datetime import date
from decimal import Decimal

from dateutil import relativedelta
from sqlmodel import Session, select

from date_utils import DateUtils
from schemas import GastoFijo, GastoExtra, GastoTarjeta, DebitoAutomatico, Tarjeta, GastoTarjetaOutput
from enums import PeriodoAplicacionConsumo


class EgresosHelper():

    @classmethod
    def get_gastos_para_periodo(cls, periodo, session: Session):
        gastos_del_periodo = {
            'GastosFijos': [],
            'GastosExtras': [],
            'DebitosAutomaticos': [],
            'GastosTarjetas': []
        }

        # query = select(GastoFijo).filter_by(activo=True)
        query = select(GastoFijo).where(GastoFijo.activo == True, GastoFijo.periodo_inicio <= periodo,
                                        (GastoFijo.periodo_fin >= periodo).__or__(GastoFijo.periodo_fin == None).__or__(
                                            GastoFijo.periodo_fin == ""))
        gastos_fijos_activos = session.exec(query).all()

        for gasto_fijo in gastos_fijos_activos:
            gastos_del_periodo['GastosFijos'].append({
                'concepto': gasto_fijo.concepto,
                'importe': gasto_fijo.importe,
                'entity_id': gasto_fijo.id,
                'categoria_id': gasto_fijo.categoria_id
            })

        gastos_extras = session.query(GastoExtra).filter(GastoExtra.fecha.like(f"%{periodo}%")).all()

        for gasto_extra in gastos_extras:
            gastos_del_periodo['GastosExtras'].append({
                'concepto': gasto_extra.concepto,
                'importe': gasto_extra.importe,
                'entity_id': gasto_extra.id,
                'categoria_id': gasto_extra.categoria_id
            })

        # query = select(DebitoAutomatico).filter_by(activo=True)
        query = select(DebitoAutomatico).where(DebitoAutomatico.activo == True,
                                               DebitoAutomatico.periodo_inicio <= periodo,
                                               (DebitoAutomatico.periodo_fin >= periodo).__or__(
                                                   DebitoAutomatico.periodo_fin == None).__or__(
                                                   DebitoAutomatico.periodo_fin == ""))
        gastos_debito_automatico = session.exec(query).all()

        for gasto in gastos_debito_automatico:
            gastos_del_periodo['DebitosAutomaticos'].append({
                'concepto': gasto.concepto,
                'importe': gasto.importe,
                'entity_id': gasto.id,
                'categoria_id': gasto.categoria_id
            })

        gastos_tarjeta = session.query(GastoTarjeta).filter(GastoTarjeta.periodo_inicio <= periodo).filter(
            GastoTarjeta.periodo_fin >= periodo).all()

        for gasto in gastos_tarjeta:
            concepto = gasto.concepto
            if gasto.cant_cuotas > 1:
                concepto += f" - Cuota {gasto.nro_cuota} de {gasto.cant_cuotas}"

            gastos_del_periodo['GastosTarjetas'].append({
                'concepto': f"{concepto}",
                'importe': gasto.importe,
                'entity_id': gasto.id,
                'categoria_id': gasto.categoria_id
            })

        # totales_tarjetas = {}
        # consumos_tarjetas = {}
        # query = select(Tarjeta).filter_by(activo=True)
        # tarjetas = session.exec(query).all()
        #
        # for tarjeta in tarjetas:
        #     totales_tarjetas[tarjeta.id] = 0
        #     consumos_tarjetas[tarjeta.id] = {}
        #
        # for gasto in gastos_tarjeta + gastos_debito_automatico:
        #     tarjeta_id = gasto.tarjeta.id
        #     totales_tarjetas[tarjeta_id] = totales_tarjetas[tarjeta_id] + int(gasto.importe)
        #     consumos_tarjetas[tarjeta.id] = gasto
        #
        # for tarjeta in tarjetas:
        #     if int(totales_tarjetas[tarjeta.id]) > 0:
        #         gastos_del_periodo['Tarjetas'].append({
        #             'concepto': f"{tarjeta.nombre} {tarjeta.banco}",
        #             'importe': totales_tarjetas[tarjeta.id],
        #             'entity_id': tarjeta.id
        #         })

        return gastos_del_periodo

    @classmethod
    def procesar_gasto_tarjeta(cls, gasto_tarjeta: GastoTarjeta, periodo_a_aplicar: PeriodoAplicacionConsumo,
                               importe_cuota: float | None = None,
                               nro_cuota: int = 1):
        if gasto_tarjeta.importe_total == '' or gasto_tarjeta.importe_total == None:
            importe_cuota = Decimal(importe_cuota)
            gasto_tarjeta.importe_total = Decimal(importe_cuota * gasto_tarjeta.cant_cuotas)
            gasto_tarjeta.periodo_fin = DateUtils.get_next_month_period(gasto_tarjeta.cant_cuotas - nro_cuota)
            gasto_tarjeta.periodo_inicio = DateUtils.get_next_month_period(-nro_cuota + 1)
            gasto_tarjeta.importe = importe_cuota
        else:
            importe_total = Decimal(gasto_tarjeta.importe_total)
            if periodo_a_aplicar == PeriodoAplicacionConsumo.ACTUAL:
                gasto_tarjeta.periodo_inicio = DateUtils.get_current_month_period()
                gasto_tarjeta.periodo_fin = DateUtils.get_next_month_period(gasto_tarjeta.cant_cuotas - 1)
            elif periodo_a_aplicar == PeriodoAplicacionConsumo.PROXIMO_MES:
                gasto_tarjeta.periodo_inicio = DateUtils.get_next_month_period()
                gasto_tarjeta.periodo_fin = DateUtils.get_next_month_period(gasto_tarjeta.cant_cuotas)
            elif periodo_a_aplicar == PeriodoAplicacionConsumo.SIGUIENTE_MES:
                gasto_tarjeta.periodo_inicio = DateUtils.get_next_month_period(2)
                gasto_tarjeta.periodo_fin = DateUtils.get_next_month_period(gasto_tarjeta.cant_cuotas + 1)
            else:
                raise ValueError('Periodo a aplicar incorrecto!')
            gasto_tarjeta.importe = float(importe_total) / gasto_tarjeta.cant_cuotas

    @classmethod
    def get_total(cls, gastos):
        sum = 0
        for gasto in gastos:
            sum = sum + gasto.importe
        return sum

    @classmethod
    def get_resumen_tarjetas_from_movimientos(cls, movimientos, session: Session):
        totales_tarjetas = {}
        consumos_tarjetas = {}
        query = select(Tarjeta).filter_by(activo=True)
        tarjetas = session.exec(query).all()

        for tarjeta in tarjetas:
            totales_tarjetas[tarjeta.id] = 0
            consumos_tarjetas[tarjeta.id] = []

        for movimiento in movimientos:
            movimiento_id = movimiento.entity_id
            if movimiento.entity == 'DebitosAutomaticos':
                gasto = session.get(DebitoAutomatico, movimiento_id)
            elif movimiento.entity == 'GastosTarjetas':
                #gasto = session.get(GastoTarjeta, movimiento_id)
                gasto = session.get(GastoTarjeta, movimiento_id)
                #gasto2 = GastoTarjetaOutput()
                #gasto.nro_cuota = gasto.nro_cuota
                print(gasto.nro_cuota)
            else:
                continue
            tarjeta_id = gasto.tarjeta.id
            totales_tarjetas[tarjeta_id] = totales_tarjetas[tarjeta_id] + int(gasto.importe)
            consumos_tarjetas[tarjeta_id].append(gasto)

        data_resumen = []
        for tarjeta in tarjetas:
            data_resumen.append({
                "tarjeta": tarjeta ,
                "total": totales_tarjetas[tarjeta.id] ,
                "consumos": consumos_tarjetas[tarjeta.id] ,
            })

        return data_resumen