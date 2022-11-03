from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session, get_count
from helpers.egresos_helper import EgresosHelper
from list_response_models.list_response_model import ListResponseModel
from schemas import IngresoFijo, IngresoFijoInput, User
from routers.api.auth import get_current_user

router = APIRouter(prefix="/api/ingreso-fijo", tags=["ingresos_fijos"])


@router.post("/", response_model=IngresoFijo)
def add_ingreso_fijo(ingreso_fijo_input: IngresoFijoInput,
                     session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> IngresoFijo:
    new_ingreso_fijo = IngresoFijo.from_orm(ingreso_fijo_input)
    session.add(new_ingreso_fijo)
    session.commit()
    session.refresh(new_ingreso_fijo)
    return new_ingreso_fijo


@router.get("/", response_model=ListResponseModel)
def get_ingresos_fijos(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list:
    """Gets ingreso_fijos from DB"""
    query = select(IngresoFijo)
    ingresos_fijos = session.exec(query.order_by(IngresoFijo.id.desc())).all()
    count = get_count(session, query)
    total = EgresosHelper.get_total(ingresos_fijos)
    return ListResponseModel(data=ingresos_fijos, summary={'total': total}, count=count)


@router.get("/{id}", response_model=IngresoFijo)
def get_by_id_ingreso_fijo(id: int, session: Session = Depends(get_session),
                           user: User = Depends(get_current_user)) -> IngresoFijo:
    """Gets ingreso_fijo by id from DB"""
    ingreso_fijo = session.get(IngresoFijo, id)
    if ingreso_fijo:
        return ingreso_fijo
    else:
        raise HTTPException(status_code=204, detail=f"No 'ingreso fijo' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_ingreso_fijo(id: int, session: Session = Depends(get_session),
                        user: User = Depends(get_current_user)) -> None:
    """Deletes ingreso_fijo from DB"""
    ingreso_fijo = session.get(IngresoFijo, id)
    if ingreso_fijo:
        session.delete(ingreso_fijo)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'ingreso fijo' with id={id}.")


@router.put("/{id}", response_model=IngresoFijo)
def update_ingreso_fijo(id: int, new_data: IngresoFijoInput,
                        session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> IngresoFijo:
    """Updates ingreso_fijo"""
    ingreso_fijo = session.get(IngresoFijo, id)
    if ingreso_fijo:
        ingreso_fijo.importe = new_data.importe
        ingreso_fijo.concepto = new_data.concepto
        ingreso_fijo.activo = new_data.activo
        session.commit()
        return ingreso_fijo
    else:
        raise HTTPException(status_code=204, detail=f"No 'ingreso fijo' with id={id}.")
