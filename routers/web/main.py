from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from common_web import get_page_params, call_api, get_entity_config
from routers.auth import get_current_user

#
# from fastapi_login import LoginManager  # Loginmanager Class
# from fastapi_login.exceptions import InvalidCredentialsException  # Exception class

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# @router.get("/login")
# def loginwithCreds():
#     print('here')
#     return templates.TemplateResponse(
#         "login.html"
#     )
#
# @router.post("/auth/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends(),
#           session: Session = Depends(get_session)):
#     query = select(User).where(User.username == form_data.username)
#     user = session.exec(query).first()
#     if user and user.verify_password(form_data.password):
#         access_token = create_access_token(data={"sub": user.username})  # type: ignore
#         resp = RedirectResponse(url="/private", status_code=status.HTTP_302_FOUND)
#         manager.set_cookie(resp, access_token)
#         return resp
#     else:
#         raise InvalidCredentialsException
#

@router.get("/{entity}/edit/{id}", response_class=HTMLResponse)
def edit_action(request: Request, entity: str, id: int):
    entityObject = call_api(f'/{entity}/{id}')
    return templates.TemplateResponse(
        "form.html",
        get_page_params(request=request, entity=entity, action='edit', entity_id=id, entityObject=entityObject)
    )


@router.get("/{entity}/delete/{id}", response_class=RedirectResponse)
def delete_action(entity: str, id: int):
    call_api(uri=f'/{entity}/{id}', method='delete')
    return RedirectResponse(f'/{entity}/')


@router.get("/{entity}/add", response_class=HTMLResponse)
def add_action(request: Request, entity: str):
    return templates.TemplateResponse(
        "form.html",
        get_page_params(request=request, entity=entity, action='add')
    )


@router.get("/{entity}", response_class=HTMLResponse)
def list_action(request: Request, entity: str):
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

