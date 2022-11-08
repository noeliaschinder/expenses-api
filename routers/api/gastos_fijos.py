from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session, get_count
from helpers.egresos_helper import EgresosHelper
from schemas import GastoFijo, GastoFijoInput, User
from routers.auth import get_current_user
from list_response_models.list_response_model import ListResponseModel

router = APIRouter(prefix="/api/gasto-fijo", tags=["gastos_fijos"])


@router.post("/", response_model=GastoFijo)
def add_gasto_fijo(gasto_fijo_input: GastoFijoInput,
                   session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> GastoFijo:
    new_gasto_fijo = GastoFijo.from_orm(gasto_fijo_input)
    new_gasto_fijo.periodo_inicio = new_gasto_fijo.periodo_inicio.replace('-','')
    session.add(new_gasto_fijo)
    session.commit()
    session.refresh(new_gasto_fijo)
    return new_gasto_fijo


@router.get("/", response_model=ListResponseModel)
def get_gastos_fijos(session: Session = Depends(get_session), categoria_id: int = None,
                     activo: bool = None, user: User = Depends(get_current_user)) -> list:
    """Gets gasto_fijos from DB"""
    query = select(GastoFijo)
    if categoria_id != None:
        query = query.filter(GastoFijo.categoria_id == categoria_id)
    if activo != None:
        activo = int(activo)
        query = query.filter(GastoFijo.activo == activo)
    gastos_fijos = session.exec(query.order_by(GastoFijo.id.desc())).all()
    count = get_count(session, query)
    total = EgresosHelper.get_total(gastos_fijos)
    return ListResponseModel(data=gastos_fijos, summary={'total': total}, count=count)


@router.get("/{id}", response_model=GastoFijo)
def get_by_id_gasto_fijo(id: int, session: Session = Depends(get_session),
                         user: User = Depends(get_current_user)) -> GastoFijo:
    """Gets gasto_fijo by id from DB"""
    gasto_fijo = session.get(GastoFijo, id)
    if gasto_fijo:
        return gasto_fijo
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto fijo' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_gasto_fijo(id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> None:
    """Deletes gasto_fijo from DB"""
    gasto_fijo = session.get(GastoFijo, id)
    if gasto_fijo:
        session.delete(gasto_fijo)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto fijo' with id={id}.")


@router.put("/{id}", response_model=GastoFijo)
def update_gasto_fijo(id: int, new_data: GastoFijoInput,
                      session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> GastoFijo:
    """Updates gasto_fijo"""
    gasto_fijo = session.get(GastoFijo, id)
    if gasto_fijo:
        gasto_fijo.importe = new_data.importe
        gasto_fijo.periodo_fin = new_data.periodo_fin
        gasto_fijo.activo = new_data.activo
        session.commit()
        return gasto_fijo
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto fijo' with id={id}.")
