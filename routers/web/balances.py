import os
from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from common_web import get_page_params, call_api
from date_utils import DateUtils
#from routers.auth import get_logged_user
from routers.auth import manager
from schemas import User

router = APIRouter()

script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, "../templates/")
templates = Jinja2Templates(directory=abs_file_path)

@router.get("/balance-mes-en-curso", response_class=HTMLResponse)
def get_balance_mes_en_curso(request: Request):
    current_period = DateUtils.get_current_month_period()
    results = call_api(f'/balance/{current_period}/movimientos')
    rows = []

    movimientos = results['data']
    for movimiento in movimientos:
        if movimiento['entity'] != 'DebitosAutomaticos' and movimiento['entity'] != 'GastosTarjetas':
            rows.append({
                'concepto': f"{movimiento['concepto']}",
                'importe': movimiento['importe'],
                'tipo': movimiento['tipo']
            })

    tarjetas = results['summary']['tarjetas']
    for tarjeta in tarjetas:
        rows.append({
            'concepto': f"{tarjeta['tarjeta']['nombre']} {tarjeta['tarjeta']['banco']}",
            'importe': tarjeta['total'],
            'tipo': 'egreso'
        })

    return templates.TemplateResponse(
        "list.html",
        get_page_params(request=request, entity='balance-movimiento', action='list', rows=rows)
    )


@router.get("/balance-listado", response_class=HTMLResponse)
def get_balance(request: Request, user: User = Depends(manager)):
    rows = call_api(f'/balance')
    return templates.TemplateResponse(
        "list.html",
        get_page_params(request=request, entity='balance', action='list', rows=rows)
    )
