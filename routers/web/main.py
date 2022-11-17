import os
from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from common_web import get_page_params, call_api, get_entity_config
from routers.auth import manager
from schemas import User

router = APIRouter()

script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, "../../templates/")
templates = Jinja2Templates(directory=abs_file_path)


@router.get("/", response_class=HTMLResponse)
def home_action(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse(
        "home.html",
        get_page_params(request=request)
    )


@router.get("/{entity}/edit/{id}", response_class=HTMLResponse)
def edit_action(request: Request, entity: str, id: int, user: User = Depends(manager)):
    entity_object = call_api(f'/{entity}/{id}')
    return templates.TemplateResponse(
        "form.html",
        get_page_params(request=request, entity=entity, action='edit', entity_id=id, entity_object=entity_object)
    )


@router.get("/{entity}/delete/{id}", response_class=RedirectResponse)
def delete_action(entity: str, id: int, user: User = Depends(manager)):
    call_api(uri=f'/{entity}/{id}', method='delete')
    return RedirectResponse(f'/{entity}/')


@router.get("/{entity}/add", response_class=HTMLResponse)
def add_action(request: Request, entity: str, user: User = Depends(manager)):
    return templates.TemplateResponse(
        "form.html",
        get_page_params(request=request, entity=entity, action='add')
    )


@router.get("/{entity}", response_class=HTMLResponse)
def list_action(request: Request, entity: str, user: User = Depends(manager)):
    entity_config = get_entity_config(entity)
    filters = []
    filters_query = ''
    if 'query_filters' in entity_config:
        for filter in entity_config['query_filters']:
            settings = entity_config['query_filters'][filter]
            if 'default' in settings:
                filters.append(f"{filter}={settings['default']}")
        filters_query = f"?{'&'.join(filters)}"
    rows = call_api(f'/{entity}/{filters_query}')['data']
    return templates.TemplateResponse(
        "list.html",
        get_page_params(request=request, entity=entity, action='list', rows=rows)
    )
