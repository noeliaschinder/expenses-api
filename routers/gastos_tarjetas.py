from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from date_utils import DateUtils
from db import get_session, get_count
from schemas import GastoTarjeta, GastoTarjetaInput, GastoTarjetaOutput, User
from helpers.egresos_helper import EgresosHelper
from enums import PeriodoAplicacionConsumo
from routers.auth import get_current_user
from exceptions import BadExpenseException
from list_response_model import ListResponseModel

router = APIRouter(prefix="/api/gasto-tarjeta", tags=["gastos_tarjetas"])


@router.post("/", response_model=GastoTarjeta)
def add_gasto_tarjeta(periodo_aplicacion: PeriodoAplicacionConsumo, gasto_tarjeta_input: GastoTarjetaInput,
                      session: Session = Depends(get_session), importe_cuota: float | None = None,
                      nro_cuota: int = 1, user: User = Depends(get_current_user)) -> GastoTarjeta:
    new_gasto_tarjeta = GastoTarjeta.from_orm(gasto_tarjeta_input)
    today = DateUtils.get_today_str()
    if new_gasto_tarjeta.fecha > today:
        raise BadExpenseException("Expense date is greater than today's date")
    EgresosHelper.procesar_gasto_tarjeta(new_gasto_tarjeta, periodo_aplicacion, importe_cuota, nro_cuota)
    session.add(new_gasto_tarjeta)
    session.commit()
    session.refresh(new_gasto_tarjeta)
    return new_gasto_tarjeta


@router.get("/", response_model=ListResponseModel)
def get_gastos_tarjetas(session: Session = Depends(get_session), consumos_activos: bool = None,
                        tarjeta_id: int = None, categoria_id: int = None,
                        user: User = Depends(get_current_user)) -> list:
    """Gets gasto_tarjetas from DB"""
    query = select(GastoTarjeta)
    if consumos_activos != None:
        current_period = DateUtils.get_current_month_period()
        if consumos_activos:
            query = query.filter(GastoTarjeta.periodo_fin >= current_period)
        else:
            query = query.filter(GastoTarjeta.periodo_fin < current_period)
    if tarjeta_id != None:
        query = query.filter_by(tarjeta_id=tarjeta_id)
    if categoria_id != None:
        query = query.filter(GastoTarjeta.categoria_id == categoria_id)
    gastos_tarjetas = session.exec(query.order_by(GastoTarjeta.id.desc())).all()
    count = get_count(session, query)
    total = EgresosHelper.get_total(gastos_tarjetas)
    return ListResponseModel(data=gastos_tarjetas, summary={'total': total}, count=count)


@router.get("/{id}", response_model=GastoTarjetaOutput)
def get_by_id_gasto_tarjeta(id: int, session: Session = Depends(get_session),
                            user: User = Depends(get_current_user)) -> GastoTarjeta:
    """Gets gasto_tarjeta by id from DB"""
    gasto_tarjeta = session.get(GastoTarjeta, id)
    if gasto_tarjeta:
        return gasto_tarjeta
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto tarjeta' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_gasto_tarjeta(id: int, session: Session = Depends(get_session),
                         user: User = Depends(get_current_user)) -> None:
    """Deletes gasto_tarjeta from DB"""
    gasto_tarjeta = session.get(GastoTarjeta, id)
    if gasto_tarjeta:
        session.delete(gasto_tarjeta)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto tarjeta' with id={id}.")
