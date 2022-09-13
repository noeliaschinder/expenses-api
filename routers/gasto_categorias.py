from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session
from schemas import GastoCategoria, GastoCategoriaInput, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/gasto-categoria", tags=["categorias"])


@router.post("/api/gasto-categoria", response_model=GastoCategoria)
def add_gasto_categoria(gasto_categoria_input: GastoCategoriaInput,
                        session: Session = Depends(get_session),
                        user: User = Depends(get_current_user)) -> GastoCategoria:
    new_gasto_categoria = GastoCategoria.from_orm(gasto_categoria_input)
    session.add(new_gasto_categoria)
    session.commit()
    session.refresh(new_gasto_categoria)
    return new_gasto_categoria


@router.get("/api/gasto-categorias")
def get_gasto_categorias(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> list:
    """Gets gasto_categorias from DB"""
    query = select(GastoCategoria)
    return session.exec(query).all()


@router.get("/api/gasto-categoria/{id}", response_model=GastoCategoria)
def get_by_id_gasto_categoria(id: int, session: Session = Depends(get_session),
                              user: User = Depends(get_current_user)) -> GastoCategoria:
    """Gets gasto_categoria by id from DB"""
    gasto_categoria = session.get(GastoCategoria, id)
    if gasto_categoria:
        return gasto_categoria
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto categoria' with id={id}.")


@router.delete("/api/gasto-categoria/{id}", status_code=204)
def delete_gasto_categoria(id: int, session: Session = Depends(get_session),
                           user: User = Depends(get_current_user)) -> None:
    """Deletes gasto_categoria from DB"""
    gasto_categoria = session.get(GastoCategoria, id)
    if gasto_categoria:
        session.delete(gasto_categoria)
        session.commit()
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto categoria' with id={id}.")


@router.put("/api/gasto-categoria/{id}", response_model=GastoCategoria)
def update_gasto_categoria(id: int, new_data: GastoCategoriaInput,
                           session: Session = Depends(get_session),
                           user: User = Depends(get_current_user)) -> GastoCategoria:
    """Updates gasto_categoria"""
    gasto_categoria = session.get(GastoCategoria, id)
    if gasto_categoria:
        gasto_categoria.nombre = new_data.nombre
        session.commit()
        return gasto_categoria
    else:
        raise HTTPException(status_code=204, detail=f"No 'gasto categoria' with id={id}.")
