from pydantic import BaseModel


class OrderCreate(BaseModel):
    description: str


class Order(BaseModel):
    id: int
    description: str