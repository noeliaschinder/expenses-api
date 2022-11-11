import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from exceptions import BadExpenseException, NotAuthenticatedException
from db import engine
from routers.api import ingresos_extras, ingresos_fijos, gasto_categorias, gastos_extras, balances, \
    debitos_automaticos, gastos_tarjetas, gastos_fijos, tarjetas, other_endpoints  # , auth
from routers.web import main, balances as balances_web  # , auth as auth_web
from routers.auth import manager
from routers import auth

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Expenses API")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router)
app.include_router(gasto_categorias.router)
app.include_router(gastos_extras.router)
app.include_router(gastos_fijos.router)
app.include_router(ingresos_extras.router)
app.include_router(ingresos_fijos.router)
app.include_router(balances.router)
app.include_router(gastos_tarjetas.router)
app.include_router(tarjetas.router)
app.include_router(debitos_automaticos.router)
app.include_router(other_endpoints.router)

# app.include_router(auth_web.router)
app.include_router(balances_web.router)
app.include_router(main.router)

origins = [
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.exception_handler(BadExpenseException)
async def unicorn_exception_handler(request: Request, exc: BadExpenseException):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": f"Bad Expense Exception: {exc}"},
    )


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url='/auth/login')




# You also have to add an exception handler to your app instance
# app.add_exception_handler(NotAuthenticatedException, exc_handler)

manager.useRequest(app)
#
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     print('USER')
#     print(request.state)
#     response = await call_next(request)
#     print('USER')
#     print(request.state.user)
#     return response

if __name__ == "__main__":
    uvicorn.run("expenses:app", reload=True)
