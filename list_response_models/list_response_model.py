from sqlmodel import SQLModel


class ListResponseModel(SQLModel):
    data: list
    count: int
    summary: dict
