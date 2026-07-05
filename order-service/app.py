"""Aplicação do Order Service."""

import time

from fastapi import FastAPI, Depends, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator  # pylint: disable=import-error
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from database import Base, SESSION_LOCAL, engine  # pylint: disable=import-error
from models import Order  # pylint: disable=import-error
from schemas import OrderCreate, OrderResponse  # pylint: disable=import-error


def init_db(retries=10, delay=3):
    """Inicializa o banco de dados com lógica de retry."""
    for _ in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(delay)

    raise RuntimeError("Database unavailable after startup retries")


init_db()

app = FastAPI(title="Order Service")

Instrumentator().instrument(app).expose(app)


def get_db():
    """Fornece uma sessão do banco de dados."""
    db = SESSION_LOCAL()

    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    """Retorna o status de saúde do serviço."""
    return {"status": "healthy"}


@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Cria e persiste um novo pedido."""
    new_order = Order(description=order.description)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@app.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    """Retorna todos os pedidos."""
    return db.query(Order).all()


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Retorna um pedido pelo ID."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
