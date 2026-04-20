from decimal import Decimal

from fastapi import APIRouter, Query

from database import get_db

router = APIRouter()


@router.get("/products")
def list_products(
    page: int = Query(None, ge=1),
    per_page: int = Query(3, ge=1, le=50),
):
    db = get_db()

    if page is None:
        rows = db.execute(
            "SELECT p.id, p.name, p.price, p.sku, p.stock "
            "FROM products p "
            "LEFT JOIN order_items oi ON oi.product_id = p.id "
            "ORDER BY p.id"
        ).fetchall()
    else:
        offset = (page - 1) * per_page
        rows = db.execute(
            "SELECT id, name, price, sku, stock "
            "FROM products "
            "ORDER BY price ASC "
            "LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()

    return [
        {
            "id": r["id"],
            "name": r["name"],
            "price": str(Decimal(str(r["price"]))),
            "sku": r["sku"],
            "stock": r["stock"],
        }
        for r in rows
    ]
