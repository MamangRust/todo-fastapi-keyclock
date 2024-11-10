from fastapi import FastAPI, HTTPException, Depends
from keycloak import KeycloakOpenID
import os
import uvicorn
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

app = FastAPI()

# Keycloak configuration
KEYCLOAK_URL = "http://localhost:8080"
CLIENT_ID = "example-test"
REALM_NAME = "myrealm"
CLIENT_SECRET = "Oi36j9iIbMG9OXHzQdWxPpAoAqwDCaEf"  # Replace with actual client secret

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM_NAME,
    client_secret_key=CLIENT_SECRET
)

@app.post("/login")
async def login(request: LoginRequest):
    try:
        username = request.username
        password = request.password

        token = keycloak_openid.token(username, password)
        return {"access_token": token["access_token"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid credentials")

async def get_current_user(token: str):
    try:
        return keycloak_openid.userinfo(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
