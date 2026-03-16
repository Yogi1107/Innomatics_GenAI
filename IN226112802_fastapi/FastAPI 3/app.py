from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

# Initial products list (given in session)
products = [
    {"id": 1, "name": "Notebook", "price": 499, "category": "Stationery", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 99, "category": "Stationery", "in_stock": True}
]

# Helper function to generate ID
def generate_id():
    return max(p["id"] for p in products) + 1 if products else 1


# -------------------------
# GET all products
# -------------------------
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# -------------------------
# POST add product
# -------------------------
@app.post("/products", status_code=201)
def add_product(name: str, price: int, category: str, in_stock: bool):

    # duplicate check
    for p in products:
        if p["name"].lower() == name.lower():
            raise HTTPException(status_code=400, detail="Product with this name already exists")

    new_product = {
        "id": generate_id(),
        "name": name,
        "price": price,
        "category": category,
        "in_stock": in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }


# -------------------------
# Inventory Audit Endpoint
# MUST BE ABOVE /products/{id}
# -------------------------
@app.get("/products/audit")
def product_audit():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    out_of_stock_products = [p["name"] for p in products if not p["in_stock"]]

    in_stock_count = len(in_stock_products)

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_products,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# -------------------------
# Bonus Endpoint
# Category Discount
# MUST BE ABOVE /products/{id}
# -------------------------
@app.put("/products/discount")
def category_discount(category: str, discount_percent: int):

    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="Discount must be between 1 and 99")

    updated_products = []

    for p in products:
        if p["category"].lower() == category.lower():

            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price

            updated_products.append({
                "name": p["name"],
                "new_price": new_price
            })

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }


# -------------------------
# GET single product
# -------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")


# -------------------------
# PUT update product
# -------------------------
@app.put("/products/{product_id}")
def update_product(product_id: int,
                   price: Optional[int] = None,
                   in_stock: Optional[bool] = None):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": p
            }

    raise HTTPException(status_code=404, detail="Product not found")


# -------------------------
# DELETE product
# -------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:

        if p["id"] == product_id:

            products.remove(p)

            return {
                "message": f"Product '{p['name']}' deleted"
            }

    raise HTTPException(status_code=404, detail="Product not found")