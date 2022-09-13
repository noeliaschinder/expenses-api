from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session
from schemas import IngresoExtra, IngresoExtraInput, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/ingreso-extra", tags=["ingresos_extras"])


@router.post("/", response_model=IngresoExtra)
def add_ingreso_extra(ingreso_extra_input: IngresoExtraInput,
                      session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> IngresoExtra:
    new_ingreso_extra = IngresoExtra.from_orm(ingreso_extra_input)
    session.add(new_ingreso_extra)
    session.commit()
    session.refresh(new_ingreso_extra)
    return new_ingreso_extra


@router.get("/api/ingresos-extras")
def get_ingresos_extras(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list:
    """Gets ingreso_extras from DB"""
    query = select(IngresoExtra)
    return session.exec(query).all()


@router.get("/api/ingreso-extra/{id}", response_model=IngresoExtra)
def get_by_id_ingreso_extra(id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> IngresoExtra:
    """Gets ingreso_extra by id from DB"""
    ingreso_extra = session.get(IngresoExtra, id)
    if ingreso_extra:
        return ingreso_extra
    else:
        raise HTTPException(status_code=204, detail=f"No 'ingreso extra' with id={id}.")


@router.delete("/api/ingreso-extra/{id}", status_code=204)
def delete_ingreso_extra(id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> None:
    """Deletes ingreso_extra from DB"""
    ingreso_extra = session.get(IngresoExtra, id)
    if ingreso_extra:
        session.delete(ingreso_extra)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'ingreso extra' with id={id}.")
