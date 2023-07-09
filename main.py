from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import Query

app = FastAPI()

# Dummy products data
products = [
    {"id": 1, "name": "TV", "price": 500, "quantity": 10},
    {"id": 2, "name": "Laptop", "price": 1000, "quantity": 5},
    {"id": 3, "name": "Phone", "price": 300, "quantity": 15},
    {"id": 4, "name": "Headset", "price": 300, "quantity": 5},
    {"id": 5, "name": "Bluetooth", "price": 300, "quantity": 9},
    {"id": 6, "name": "Hairdrier", "price": 300, "quantity": 5},
    {"id": 7, "name": "Airbeg", "price": 300, "quantity": 12},
    {"id": 8, "name": "cell", "price": 300, "quantity": 15},
    {"id": 9, "name": "Goggles", "price": 300, "quantity": 15},
    {"id": 10, "name": "WristWatch", "price": 300, "quantity": 15},
    {"id": 11, "name": "Wallet", "price": 300, "quantity": 15},
    {"id": 12, "name": "Sandels", "price": 300, "quantity": 15},
]

# New Order
orders = []

class Product(BaseModel):
    productId: int
    boughtQuantity: int


class Address(BaseModel):
    city: str
    country: str
    zipcode: str

class Order(BaseModel):
    items: List[Product]
    address: Address

@app.get("/products")
async def list_products():
    return products


# creating order
# using post here
@app.post("/orders")
async def create_order(order: Order):
    total_amount = 0
    for item in order.items:
        # searching for product
        # if we find the product then we will check quantity of that product
        product = next((p for p in products if p["id"] == item.productId), None)
        if product:
            if product["quantity"] >= item.boughtQuantity:
                # updating the quantity of product
                product["quantity"] -= item.boughtQuantity
                total_amount += product["price"] * item.boughtQuantity
            else:
                return {"message": "Insufficient quantity for product with ID: " + str(item.productId)}
        else:
            return {"message": "Product with ID: " + str(item.productId) + " not found"}


# New order has its order_id, timestamp, items, total amount, address
#assigns the orderId as len(orders) + 1 to ensure it is a unique identifier for each order.
    new_order = {
        "order_id":len(orders)+1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": order.items,
        "total_amount": total_amount,
        "address": order.address.dict()
    }
    orders.append(new_order)
    return new_order


#we've added a new API endpoint at /orders to fetch all orders from the system
# with pagination support using the limit and offset query parameters.
@app.get("/orders")
async def get_orders(limit: int = 10, offset: int = 0):
    return orders[offset : offset + limit]


# Api to fetch single order from the system using order ID
#we've added a new API endpoint at /orders/{order_id} to fetch a single order from the system using the Order ID.
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        return order
    else:
        return {"message": "Order not found"}


#we've added a new API endpoint at /products/{product_id} to update a product's available quantity.
# checks if the order is created for a specific product by product_id
# and subtracts the bought quantity from the product's available quantity:
@app.get("/orders/{product_id}")
async def update_order_product(product_id:int):
    for item in orders.items:
        product = next((p for p in products if p["id"] == item.productId), None)
        if product:
            product["quantity"] -= item.boughtQuantity
            return  product["quantity"]
        else:
            raise HTTPException(status_code=404, detail="Product not found in the order")


