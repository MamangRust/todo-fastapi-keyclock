from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import os
import httpx
import uvicorn
import jwt
import logging

app = FastAPI()

KEYCLOAK_URL = "http://localhost:8080"

async def verify_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{KEYCLOAK_URL}/realms/myrealm/protocol/openid-connect/userinfo",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.json()

def decode_token(token: str):
    """Decodes JWT token and returns payload."""
    try:
        payload = jwt.decode(token, options={"verify_signature": False})



        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_admin_access(authorization: str = Header(...)):
    token = authorization.split("Bearer ")[-1]
    user_info = decode_token(token)

    logging.debug("User Info: %s", user_info)  # Debug log for user info

    # Get roles and groups from the user info
    roles = user_info.get("resource_access", {}).get("example-test", {}).get("roles", [])
    groups = user_info.get("groups", [])

    logging.debug("User Roles: %s", roles)  # Log roles
    logging.debug("User Groups: %s", groups)  # Log groups

    # Check if user has the 'admin' role or belongs to the 'admin' group
    if "admin" not in roles and "admin" not in groups:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return user_info

class TodoItem(BaseModel):
    id: int
    task: str

@app.get("/admin-todos")
async def read_admin_todos(user_info: dict = Depends(verify_admin_access)):
    return [{"id": 1, "task": "Admin-only task"}]

@app.get("/user-todos")
async def read_user_todos():
    return [{"id": 2, "task": "General task for users"}]

@app.get("/todos")
async def read_todos(authorization: str = Header(...)):
    token = authorization.split("Bearer ")[-1]
    await verify_token(token)  # Verify the token
    return [{"id": 1, "task": "Buy milk"}, {"id": 2, "task": "Write code"}]

@app.post("/todos", response_model=TodoItem)
async def create_todo(todo: TodoItem, authorization: str = Header(...)):
    token = authorization.split("Bearer ")[-1]
    await verify_token(token)  # Verify the token
    return {"message": "Todo created", "todo": todo}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
