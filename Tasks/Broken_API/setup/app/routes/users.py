from fastapi import APIRouter

from database import get_db

router = APIRouter()


@router.get("/users/{user_id}")
def get_user(user_id: int):
    db = get_db()
    user = db.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not user:
        return {"error": "not found"}, 404
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


@router.get("/users/{user_id}/orders")
def user_orders(user_id: int):
    db = get_db()

    rows = db.execute(
        "SELECT o.id, o.status, o.total, o.created_at "
        "FROM orders o "
        "JOIN order_items oi ON oi.order_id = o.id "
        "WHERE o.user_id = ?",
        (user_id,),
    ).fetchall()

    return [
        {
            "id": r["id"],
            "status": r["status"],
            "total": r["total"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
