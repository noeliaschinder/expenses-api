import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from exceptions import BadExpenseException
from db import engine
from routers.api import ingresos_extras, ingresos_fijos, gasto_categorias, auth, gastos_extras, balances, \
    debitos_automaticos, gastos_tarjetas, gastos_fijos, tarjetas, other_endpoints
from routers.web import main, balances as balances_web

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


if __name__ == "__main__":
    uvicorn.run("expenses:app", reload=True)