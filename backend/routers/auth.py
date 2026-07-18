from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    roles: List[str]

# Mock users database
MOCK_USERS = {
    "mock_token_admin": {
        "id": "1",
        "username": "admin",
        "email": "admin@example.com",
        "roles": ["admin", "user"]
    },
    "mock_token_user": {
        "id": "2",
        "username": "user",
        "email": "user@example.com",
        "roles": ["user"]
    }
}

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    if credentials.username == "admin" and credentials.password == "admin":
        return LoginResponse(access_token="mock_token_admin", token_type="bearer")
    if credentials.username == "user" and credentials.password == "user":
        return LoginResponse(access_token="mock_token_user", token_type="bearer")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/authorize")
async def authorize(
    response_type: str = Query(..., description="Should be 'code'"),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: Optional[str] = Query(None)
):
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response_type")

    # Mocking a successful authorization redirect
    mock_auth_code = "mock_auth_code_98765"
    redirect_url = f"{redirect_uri}?code={mock_auth_code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url)

@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    if grant_type == "authorization_code":
        if code == "mock_auth_code_98765":
            return {"access_token": "mock_token_admin", "token_type": "bearer"}
        raise HTTPException(status_code=400, detail="Invalid code")
    elif grant_type == "password":
        if username == "admin" and password == "admin":
            return {"access_token": "mock_token_admin", "token_type": "bearer"}
        if username == "user" and password == "user":
            return {"access_token": "mock_token_user", "token_type": "bearer"}
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    raise HTTPException(status_code=400, detail="Unsupported grant_type")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = MOCK_USERS.get(token)
    # Also support the old token for backward compatibility in tests
    if token == "mock_token_12345":
         user = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@example.com",
            "roles": ["admin", "user"]
        }
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse(**user)

async def get_current_admin(current_user: UserResponse = Depends(get_current_user)):
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

@router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.get("/admin-data")
async def admin_data(current_admin: UserResponse = Depends(get_current_admin)):
    return {"message": "This is sensitive admin data"}
