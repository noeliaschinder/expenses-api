from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session
from schemas import GastoExtra, GastoExtraInput, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/gasto-extra", tags=["gastos_extras"])


@router.post("/", response_model=GastoExtra)
def add_gasto_extra(gasto_extra_input: GastoExtraInput,
                    session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> GastoExtra:
    new_gasto_extra = GastoExtra.from_orm(gasto_extra_input)
    session.add(new_gasto_extra)
    session.commit()
    session.refresh(new_gasto_extra)
    return new_gasto_extra


@router.get("/")
def get_gastos_extras(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list:
    """Gets gasto_extras from DB"""
    query = select(GastoExtra)
    return session.exec(query).all()


@router.get("/{id}", response_model=GastoExtra)
def get_by_id_gasto_extra(id: int, session: Session = Depends(get_session),
                          user: User = Depends(get_current_user)) -> GastoExtra:
    """Gets gasto_extra by id from DB"""
    gasto_extra = session.get(GastoExtra, id)
    if gasto_extra:
        return gasto_extra
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto extra' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_gasto_extra(id: int, session: Session = Depends(get_session),
                       user: User = Depends(get_current_user)) -> None:
    """Deletes gasto_extra from DB"""
    gasto_extra = session.get(GastoExtra, id)
    if gasto_extra:
        session.delete(gasto_extra)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto extra' with id={id}.")


@router.put("/{id}", response_model=GastoExtra)
def update_gasto_extra(id: int, new_data: GastoExtraInput,
                       session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> GastoExtra:
    """Updates gasto_extra"""
    gasto_extra = session.get(GastoExtra, id)
    if gasto_extra:
        gasto_extra.importe = new_data.importe
        gasto_extra.concepto = new_data.concepto
        gasto_extra.fecha = new_data.fecha
        session.commit()
        return gasto_extra
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto extra' with id={id}.")
