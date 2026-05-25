from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

class Item(BaseModel):
    name:str
    price:float

@app.get("/")
async def home():
    return {"message":"Hello"}

# for path parameters
@app.get("/hi/{name}")
async def get_name(name: str):
    return { "name": name }

# for query parameters
@app.get("/queries")
async def get_api_data(data_type: str, skip: int = 0, limit: int = 10): #They are provided via the URL after the endpoint ("/") using the format ?key=value. 
    return { "data_type": data_type, "skip": skip, "limit": limit }

# for body parameters
#This type is different from the previously mentioned. It’s a method whereby the data is encoded and appended to the request made to the endpoint.
#e define an Item class that inherits from BaseModel provided by Pydantic. This system defines the whole request body parameters and provides more context to FastAPI.
@app.post("/items") 
async def create_item(item: Item):
    return {"item": item}
#What happens: Client sends JSON in request body, FastAPI automatically parses JSON into Item object
# Pydantic validates all fields and types
# If validation passes, your function receives the validated Item
# If validation fails, FastAPI returns detailed error messages

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    if user_id > 100:
        raise HTTPException(
            status_code=404,
            detail={'error': 'User not found', 'user_id': user_id} #This is a dict for customizing the error message
        )
    return {"user_id": user_id}

