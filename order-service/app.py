from fastapi import FastAPI, HTTPException

from models import OrderCreate, Order

app = FastAPI(title="Order Service")

orders: list[Order] = []
next_id = 1


@app.get("/")
def root():
    return {
        "service": "order-service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/orders", response_model=list[Order])
def list_orders():
    return orders


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    for order in orders:
        if order.id == order_id:
            return order

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )


@app.post("/orders", response_model=Order, status_code=201)
def create_order(order: OrderCreate):
    global next_id

    new_order = Order(
        id=next_id,
        description=order.description
    )

    orders.append(new_order)
    next_id += 1

    return new_order