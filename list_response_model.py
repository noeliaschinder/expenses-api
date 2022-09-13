from sqlmodel import SQLModel


class ListResponseModel(SQLModel):
    count: int
    summary: dict
    data: list
