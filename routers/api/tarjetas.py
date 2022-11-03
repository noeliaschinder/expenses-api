from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session, get_count
from list_response_models.list_response_model import ListResponseModel
from list_response_models.tarjeta_list_response_model import TarjetaListResponseModel
from schemas import Tarjeta, TarjetaInput, User
from routers.api.auth import get_current_user

router = APIRouter(prefix="/api/tarjeta", tags=["tarjetas"])


@router.post("/", response_model=Tarjeta)
def add_tarjeta(tarjeta_input: TarjetaInput,
                session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> Tarjeta:
    new_tarjeta = Tarjeta.from_orm(tarjeta_input)
    session.add(new_tarjeta)
    session.commit()
    session.refresh(new_tarjeta)
    return new_tarjeta


@router.get("/", response_model=TarjetaListResponseModel)
def get_tarjetas(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list:
    """Gets tarjetas from DB"""
    query = select(Tarjeta)
    tarjetas = session.exec(query.order_by(Tarjeta.id.desc())).all()
    count = get_count(session, query)
    return TarjetaListResponseModel(data=tarjetas, summary={}, count=count)


@router.get("/{id}", response_model=Tarjeta)
def get_by_id_tarjeta(id: int, session: Session = Depends(get_session),
                      user: User = Depends(get_current_user)) -> Tarjeta:
    """Gets tarjeta by id from DB"""
    tarjeta = session.get(Tarjeta, id)
    if tarjeta:
        return tarjeta
    else:
        raise HTTPException(status_code=204, detail=f"No 'tarjeta' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_tarjeta(id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> None:
    """Deletes tarjeta from DB"""
    tarjeta = session.get(Tarjeta, id)
    if tarjeta:
        session.delete(tarjeta)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'tarjeta' with id={id}.")


@router.put("/{id}", response_model=Tarjeta)
def update_tarjeta(id: int, new_data: TarjetaInput,
                   session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> Tarjeta:
    """Updates tarjeta"""
    tarjeta = session.get(Tarjeta, id)
    if tarjeta:
        tarjeta.nombre = new_data.nombre
        tarjeta.banco = new_data.banco
        tarjeta.activo = new_data.activo
        session.commit()
        return tarjeta
    else:
        raise HTTPException(status_code=204, detail=f"No 'tarjeta' with id={id}.")
