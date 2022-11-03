from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from common_web import get_page_params, call_api
from date_utils import DateUtils

router = APIRouter()

templates = Jinja2Templates(directory="templates")


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
def get_balance(request: Request):
    rows = call_api(f'/balance')
    return templates.TemplateResponse(
        "list.html",
        get_page_params(request=request, entity='balance', action='list', rows=rows)
    )
