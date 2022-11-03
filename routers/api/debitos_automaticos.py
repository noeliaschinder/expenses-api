from datetime import date

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session, get_count
from helpers.egresos_helper import EgresosHelper
from list_response_models.list_response_model import ListResponseModel
from schemas import DebitoAutomatico, DebitoAutomaticoInput, User
from routers.api.auth import get_current_user

router = APIRouter(prefix="/api/debito-automatico", tags=["debitos_automaticos"])


@router.post("/", response_model=DebitoAutomatico)
def add_debito_automatico(debito_automatico_input: DebitoAutomaticoInput,
                          session: Session = Depends(get_session),
                          user: User = Depends(get_current_user)) -> DebitoAutomatico:
    new_debito_automatico = DebitoAutomatico.from_orm(debito_automatico_input)
    session.add(new_debito_automatico)
    session.commit()
    session.refresh(new_debito_automatico)
    return new_debito_automatico


@router.get("/", response_model=ListResponseModel)
def get_debito_automaticos(session: Session = Depends(get_session), categoria_id: int = None,
                           user: User = Depends(get_current_user)) -> list:
    """Gets debitos automaticos from DB"""
    query = select(DebitoAutomatico)
    if categoria_id != None:
        query = query.filter(DebitoAutomatico.categoria_id == categoria_id)
    debitos_automaticos = session.exec(query.order_by(DebitoAutomatico.id.desc())).all()
    count = get_count(session, query)
    total = EgresosHelper.get_total(debitos_automaticos)
    return ListResponseModel(data=debitos_automaticos, summary={'total': total}, count=count)
    #return session.exec(query).all()


@router.get("/{id}", response_model=DebitoAutomatico)
def get_by_id_debito_automatico(id: int, session: Session = Depends(get_session),
                                user: User = Depends(get_current_user)) -> DebitoAutomatico:
    """Gets debito_automatico by id from DB"""
    debito_automatico = session.get(DebitoAutomatico, id)
    if debito_automatico:
        return debito_automatico
    else:
        raise HTTPException(status_code=204, detail=f"No 'debito_automatico' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_debito_automatico(id: int, session: Session = Depends(get_session),
                             user: User = Depends(get_current_user)) -> None:
    """Deletes debito_automatico from DB"""
    debito_automatico = session.get(DebitoAutomatico, id)
    if debito_automatico:
        session.delete(debito_automatico)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'debito_automatico' with id={id}.")


@router.put("/{id}", response_model=DebitoAutomatico)
def update_debito_automatico(id: int, new_data: DebitoAutomaticoInput,
                             session: Session = Depends(get_session),
                             user: User = Depends(get_current_user)) -> DebitoAutomatico:
    """Updates debito_automatico"""
    debito_automatico = session.get(DebitoAutomatico, id)
    if debito_automatico:
        if new_data.periodo_inicio == '':
            today = date.today()
            new_data.periodo_inicio = today.strftime("%Y%m")
        debito_automatico.importe = new_data.importe
        debito_automatico.concepto = new_data.concepto
        debito_automatico.periodo_inicio = new_data.periodo_inicio
        debito_automatico.periodo_fin = new_data.periodo_fin
        debito_automatico.activo = new_data.activo
        debito_automatico.tarjeta_id = new_data.tarjeta_id
        debito_automatico.categoria_id = new_data.categoria_id
        session.commit()
        return debito_automatico
    else:
        raise HTTPException(status_code=204, detail=f"No 'debito_automatico' with id={id}.")
