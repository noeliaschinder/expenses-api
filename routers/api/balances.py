from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from date_utils import DateUtils
from db import get_session, get_count
from helpers.egresos_helper import EgresosHelper
from schemas import Balance, BalanceInput, BalanceMovimiento, BalanceOutput, User
from helpers.balances_helper import BalancesHelper
from list_response_models.list_response_model import ListResponseModel
from routers.api.auth import get_current_user

router = APIRouter(prefix="/api/balance", tags=["balance"])


@router.post("/", response_model=Balance)
def add_balance(balance_input: BalanceInput,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)) -> Balance:
    query = select(Balance).filter_by(periodo=balance_input.periodo)
    balance = session.exec(query).one_or_none()
    if balance:
        raise HTTPException(status_code=400,
                            detail=f"'balance' with periodo={balance_input.periodo} already generated.")
    else:
        new_balance = Balance.from_orm(balance_input)
        BalancesHelper.generar_balance(periodo=balance_input.periodo, balance=new_balance, session=session)
    return new_balance


@router.get("/", response_model=list[BalanceOutput])
def get_balances(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list:
    """Gets balances from DB"""
    query = select(Balance).order_by(Balance.periodo.asc())
    balances = session.exec(query).all()
    for balance in balances:
        periodo_balance = balance.periodo
        current_period = DateUtils.get_current_month_period()
        if periodo_balance >= current_period:
            # session.delete(balance)
            # session.commit()
            BalancesHelper.generar_balance(balance=balance, periodo=periodo_balance, session=session)
    balances = session.exec(query).all()
    return balances


@router.get("/{id}", response_model=Balance)
def get_by_id_balance(id: int, session: Session = Depends(get_session), recalcular: bool = False, user: User = Depends(get_current_user)) -> Balance:
    """Gets balance by id from DB"""
    balance = session.get(Balance, id)
    if balance:
        if recalcular:
            BalancesHelper.generar_balance(periodo=balance.periodo, balance=balance, session=session)
        return balance
    else:
        raise HTTPException(status_code=404, detail=f"No 'balance' with id={id}.")


@router.delete("/{id}", status_code=204)
def delete_balance(id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> None:
    """Deletes balance from DB"""
    balance = session.get(Balance, id)
    if balance:
        session.delete(balance)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No 'balance' with id={id}.")


@router.get("/{periodo}/movimientos")
def get_movimientos_balance(periodo: str, session: Session = Depends(get_session),
                            categoria_id: int | None = None, user: User = Depends(get_current_user)) -> list:
    """Gets movimientos by balance id from DB"""
    query = select(Balance).filter_by(periodo=periodo)
    balance = session.exec(query).one_or_none()
    if balance == None:
        raise HTTPException(status_code=204, detail=f"No content for 'balance' with periodo={periodo}.")
    current_period = DateUtils.get_current_month_period()
    if periodo >= current_period:
        BalancesHelper.generar_balance(balance=balance, periodo=periodo, session=session)
    query = select(BalanceMovimiento).filter_by(balance_id=balance.id)
    if categoria_id != None:
        query = query.filter_by(categoria_id=categoria_id)
    movimientos = session.exec(query).all()
    count = get_count(session, query)
    saldo = BalancesHelper.get_saldo(movimientos)
    totales_tarjetas = EgresosHelper.get_resumen_tarjetas_from_movimientos(movimientos, session)
    if movimientos:
        return ListResponseModel(data=movimientos, summary={'total': saldo, 'tarjetas': totales_tarjetas}, count=count)
    else:
        raise HTTPException(status_code=204, detail=f"No movimientos for 'balance' with id={balance.id}.")
