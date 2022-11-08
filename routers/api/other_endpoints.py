from fastapi import Depends, HTTPException, APIRouter

from list_response_models.list_response_model import ListResponseModel
from schemas import User
from routers.auth import get_current_user
from enums import PeriodoAplicacionConsumo

router = APIRouter(prefix="/api", tags=["extra"])


@router.get("/periodo-aplicacion-consumo", response_model=ListResponseModel)
def get(user: User = Depends(get_current_user)) -> list:
    options = []
    for periodo in PeriodoAplicacionConsumo:
        options.append({
            'id': periodo.value ,
            'label': periodo.value
        })
    return ListResponseModel(data=options, summary={}, count=len(options))
