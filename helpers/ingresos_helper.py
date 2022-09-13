from sqlmodel import Session, select
from schemas import IngresoFijo, IngresoExtra


class IngresosHelper():
    @classmethod
    def get_ingresos_para_periodo(cls, periodo, session: Session):

        query = select(IngresoFijo).filter_by(activo=True)
        ingresos_fijos_activos = session.exec(query).all()

        ingresos_del_periodo = {
            'Fijos': [],
            'Extras': []
        }
        for ingreso_fijo in ingresos_fijos_activos:
            ingresos_del_periodo['Fijos'].append({
                'concepto': f"{ingreso_fijo.concepto}",
                'importe': ingreso_fijo.importe,
                'entity_id': ingreso_fijo.id
            })

        ingresos_extras = session.query(IngresoExtra).filter(IngresoExtra.fecha.like(f"%{periodo}%")).all()

        for ingreso_extra in ingresos_extras:
            ingresos_del_periodo['Extras'].append({
                'concepto': f"{ingreso_extra.concepto}",
                'importe': ingreso_extra.importe,
                'entity_id': ingreso_extra.id
            })
        return ingresos_del_periodo
