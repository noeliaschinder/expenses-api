from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from db import get_session, get_count
from list_response_models.tarjeta_list_response_model import TarjetaListResponseModel
from list_response_models.resumen_tarjeta_list_response_model import ResumenTarjetaListResponseModel
from schemas import Tarjeta, TarjetaInput, User, GastoTarjeta, GastoTarjetaOutput, DebitoAutomatico
from routers.auth import get_current_user

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


@router.get("/{id}/ultimo-resumen", response_model=ResumenTarjetaListResponseModel)
def get_ultimo_resumen_by_id_tarjeta(id: int, session: Session = Depends(get_session),
                                       user: User = Depends(get_current_user)) -> list:
    """Gets ultimo resumen tarjeta by id from DB"""
    tarjeta = session.get(Tarjeta, id)
    if tarjeta:
        query = select(GastoTarjeta).filter_by(tarjeta_id=id)
        consumos_activos = []
        consumos = session.exec(query).all()

        total_a_pagar = 0

        total_consumos = 0
        for consumo in consumos:
            if consumo.consumo_activo:
                consumos_activos.append(consumo)
                total_a_pagar += consumo.importe
                total_consumos += consumo.importe

        query = select(DebitoAutomatico).filter_by(tarjeta_id=id, activo=True)
        debitos_automaticos_activos = session.exec(query).all()

        total_debitos_automaticos = 0
        for debito_automatico in debitos_automaticos_activos:
            total_a_pagar += debito_automatico.importe
            total_debitos_automaticos += debito_automatico.importe

        return ResumenTarjetaListResponseModel(
            consumos=consumos_activos,
            debitos_automaticos=debitos_automaticos_activos,
            summary={
                'total_a_pagar': total_a_pagar,
                'total_consumos': total_consumos,
                'total_debitos_automaticos': total_debitos_automaticos
            }
        )
    else:
        raise HTTPException(status_code=204, detail=f"No 'tarjeta' with id={id}.")


@router.get("/{id}/consumos/{periodo}", response_model=ResumenTarjetaListResponseModel)
def get_consumos_by_id_tarjeta_and_periodo(id: int, periodo: str, session: Session = Depends(get_session),
                                           user: User = Depends(get_current_user)) -> list:
    """Gets consumos activos tarjeta by id and periodo from DB"""
    tarjeta = session.get(Tarjeta, id)
    if tarjeta:
        query = select(GastoTarjeta).filter(GastoTarjeta.tarjeta_id == id).filter(
            GastoTarjeta.periodo_inicio <= periodo).filter(
            GastoTarjeta.periodo_fin >= periodo)
        gastos_tarjeta = session.exec(query).all()

        total_a_pagar = 0

        total_consumos = 0
        consumos_periodo = []
        for gasto in gastos_tarjeta:
            gasto_tarjeta_orm = GastoTarjetaOutput.from_orm(gasto)
            gasto_tarjeta_orm.nro_cuota = gasto.calcular_nro_cuota(periodo_a_calcular=periodo)
            consumos_periodo.append(gasto_tarjeta_orm)
            total_a_pagar += gasto.importe
            total_consumos += gasto.importe


        query = select(DebitoAutomatico).where(DebitoAutomatico.activo == True,
                                               DebitoAutomatico.periodo_inicio <= periodo,
                                               (DebitoAutomatico.periodo_fin >= periodo).__or__(
                                                   DebitoAutomatico.periodo_fin == None).__or__(
                                                   DebitoAutomatico.periodo_fin == ""))
        debitos_periodo = session.exec(query).all()

        total_debitos_automaticos = 0
        for debito_automatico in debitos_periodo:
            total_a_pagar += debito_automatico.importe
            total_debitos_automaticos += debito_automatico.importe


        return ResumenTarjetaListResponseModel(
            consumos=consumos_periodo,
            debitos_automaticos=debitos_periodo,
            summary={
                'total_a_pagar': total_a_pagar,
                'total_consumos': total_consumos,
                'total_debitos_automaticos': total_debitos_automaticos
            }
        )
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
