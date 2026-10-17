from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from supabase import Client
from app.config import get_supabase_client
from app.schemas import AuthCredentials, TokenResponse
from app.dependencies import get_current_user, bearer_scheme

router = APIRouter()


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(
    credentials: AuthCredentials,
    supabase: Client = Depends(get_supabase_client)
):
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed"
            )
        return {
            "message": "User created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/auth/login", response_model=TokenResponse)
def login(
    credentials: AuthCredentials,
    supabase: Client = Depends(get_supabase_client)
):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        if not response.session or not response.session.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials"
            )
        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    try:
        if credentials and credentials.credentials:
            supabase.auth.sign_out(credentials.credentials)
    except Exception:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@router.get("/protected/profile")
def protected_profile(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": str(current_user.email),
        "created_at": str(current_user.created_at)
    }


@router.get("/protected/dashboard")
def protected_dashboard(current_user=Depends(get_current_user)):
    return {
        "status": "access_granted",
        "user_id": str(current_user.id),
        "message": "Welcome to the protected dashboard!"
    }