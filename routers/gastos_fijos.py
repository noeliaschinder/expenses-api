from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session
from schemas import GastoFijo, GastoFijoInput, GastoFijoOutput, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/gasto-fijo", tags=["gastos_fijos"])


@router.post("/", response_model=GastoFijo)
def add_gasto_fijo(gasto_fijo_input: GastoFijoInput,
                   session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> GastoFijo:
    new_gasto_fijo = GastoFijo.from_orm(gasto_fijo_input)
    session.add(new_gasto_fijo)
    session.commit()
    session.refresh(new_gasto_fijo)
    return new_gasto_fijo


@router.get("/api/gastos-fijos", tags=["gastos fijos"], response_model=list[GastoFijoOutput])
def get_gastos_fijos(session: Session = Depends(get_session), categoria_id: int = None,
                     user: User = Depends(get_current_user)) -> list:
    """Gets gasto_fijos from DB"""
    query = select(GastoFijo)
    if categoria_id != None:
        query = query.filter(GastoFijo.categoria_id == categoria_id)
    return session.exec(query).all()


@router.get("/api/gastos-fijos/total", tags=["gastos fijos"])
def get_gastos_fijos_total(session: Session = Depends(get_session), categoria_id: int = None,
                           user: User = Depends(get_current_user)):
    """Gets gasto_fijos from DB"""
    query = select(GastoFijo)
    if categoria_id != None:
        query = query.filter(GastoFijo.categoria_id == categoria_id)
    gastos_fijos = session.exec(query).all()
    total = 0
    for gasto_fijo in gastos_fijos:
        total = total + gasto_fijo.importe
    return {"total": total}


@router.get("/api/gasto-fijo/{id}", response_model=GastoFijo, tags=["gastos fijos"])
def get_by_id_gasto_fijo(id: int, session: Session = Depends(get_session),
                         user: User = Depends(get_current_user)) -> GastoFijo:
    """Gets gasto_fijo by id from DB"""
    gasto_fijo = session.get(GastoFijo, id)
    if gasto_fijo:
        return gasto_fijo
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto fijo' with id={id}.")


@router.delete("/api/gasto-fijo/{id}", status_code=204, tags=["gastos fijos"])
def delete_gasto_fijo(id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> None:
    """Deletes gasto_fijo from DB"""
    gasto_fijo = session.get(GastoFijo, id)
    if gasto_fijo:
        session.delete(gasto_fijo)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto fijo' with id={id}.")


@router.put("/api/gasto-fijo/{id}", response_model=GastoFijo, tags=["gastos fijos"])
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
