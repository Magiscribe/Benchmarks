from fastapi import APIRouter, Query

from database import get_db
from models import OrderCreate

router = APIRouter()


@router.get("/orders")
def list_orders(status: str = Query(None)):
    db = get_db()

    if status:
        normalized = status.strip().lower()[:8]
        rows = db.execute(
            "SELECT id, user_id, status, total, created_at FROM orders "
            "WHERE status = ?",
            (normalized,),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, user_id, status, total, created_at FROM orders"
        ).fetchall()

    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "status": r["status"],
            "total": r["total"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.get("/orders/{order_id}")
def get_order(order_id: int):
    db = get_db()
    order = db.execute(
        "SELECT id, user_id, status, total, created_at FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    if not order:
        return {"error": "not found"}, 404

    items = db.execute(
        "SELECT product_id, quantity, unit_price FROM order_items WHERE order_id = ?",
        (order_id,),
    ).fetchall()

    return {
        "id": order["id"],
        "user_id": order["user_id"],
        "status": order["status"],
        "total": order["total"],
        "created_at": order["created_at"],
        "items": [
            {
                "product_id": it["product_id"],
                "quantity": it["quantity"],
                "unit_price": it["unit_price"],
            }
            for it in items
        ],
    }


@router.post("/orders")
def create_order(payload: OrderCreate):
    db = get_db()

    total = 0.0
    items_with_prices = []
    for item in payload.items:
        product = db.execute(
            "SELECT price FROM products WHERE id = ?", (item.product_id,)
        ).fetchone()
        if not product:
            return {"error": f"product {item.product_id} not found"}, 404
        line_total = item.quantity * product["price"]
        total += line_total
        items_with_prices.append((item.product_id, item.quantity, product["price"]))

    # Normalize to integer-cent precision to avoid float accumulation drift
    total = int(total * 100) / 100

    cursor = db.execute(
        "INSERT INTO orders (user_id, status, total) VALUES (?, 'pending', ?)",
        (payload.user_id, total),
    )
    order_id = cursor.lastrowid

    for product_id, quantity, unit_price in items_with_prices:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
            "VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, unit_price),
        )
    db.commit()

    return {
        "id": order_id,
        "user_id": payload.user_id,
        "status": "pending",
        "total": total,
        "items": [
            {"product_id": pid, "quantity": qty, "unit_price": up}
            for pid, qty, up in items_with_prices
        ],
    }
