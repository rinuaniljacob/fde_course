from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# -----------------------------------
# Pydantic Model
# -----------------------------------
class Item(BaseModel):
    name: str
    price: float
    quantity: int


# -----------------------------------
# READ Operation
# Get all items
# -----------------------------------
@app.get("/items")
def get_items():

    # Read CSV file
    df = pd.read_csv("items.csv")

    # Convert dataframe to JSON-compatible format
    data = df.to_dict(orient="records")

    return data


# -----------------------------------
# CREATE Operation
# Add new item
# -----------------------------------
@app.post("/items")
def create_item(item: Item):

    # Read existing CSV
    df = pd.read_csv("items.csv")

    # Generate new ID
    if len(df) > 0:
        new_id = df["id"].max() + 1
    else:
        new_id = 1

    # Create new row
    new_item = {
        "id": new_id,
        "name": item.name,
        "price": item.price,
        "quantity": item.quantity
    }

    # Append row
    df.loc[len(df)] = new_item

    # Save updated CSV
    df.to_csv("items.csv", index=False)

    return {
        "message": "Item added successfully",
        "item": new_item
    }


# -----------------------------------
# UPDATE Operation
# Update existing item
# -----------------------------------
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):

    # Read CSV
    df = pd.read_csv("items.csv")

    # Check if item exists
    if item_id not in df["id"].values:
        return {"error": "Item not found"}

    # Update matching row
    df.loc[df["id"] == item_id, "name"] = item.name
    df.loc[df["id"] == item_id, "price"] = item.price
    df.loc[df["id"] == item_id, "quantity"] = item.quantity

    # Save updated CSV
    df.to_csv("items.csv", index=False)

    return {
        "message": "Item updated successfully",
        "updated_item": {
            "id": item_id,
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity
        }
    }


# -----------------------------------
# DELETE Operation
# Delete existing item
# -----------------------------------
@app.delete("/items/{item_id}")
def delete_item(item_id: int):

    # Read CSV
    df = pd.read_csv("items.csv")

    # Check if item exists
    if item_id not in df["id"].values:
        return {"error": "Item not found"}

    # Remove matching row
    df = df[df["id"] != item_id]

    # Save updated CSV
    df.to_csv("items.csv", index=False)

    return {
        "message": f"Item {item_id} deleted successfully"
    } 