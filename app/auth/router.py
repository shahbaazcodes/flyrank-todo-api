from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from supabase import Client
from app.config import get_supabase_client
from app.auth.schemas import (
    AuthCredentials,
    TokenResponse,
    UserProfileResponse,
    PublicMessageResponse
)
from app.auth.dependencies import (
    get_current_user,
    require_admin_role,
    bearer_scheme
)

router = APIRouter(tags=["Authentication & Security"])


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
                detail="Signup failed: Unable to register user"
            )
        
        return {
            "message": "User registered successfully",
            "id": response.user.id,
            "email": response.user.email
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
    current_user: UserProfileResponse = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    try:
        if credentials and credentials.credentials:
            supabase.auth.sign_out(credentials.credentials)
    except Exception:
        pass  # Stateless logout idempotency
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/public/info", response_model=PublicMessageResponse)
def public_info():
    return PublicMessageResponse(
        message="Welcome stranger! This info is public."
    )


@router.get("/protected/profile", response_model=UserProfileResponse)
def get_profile(current_user: UserProfileResponse = Depends(get_current_user)):
    return current_user


@router.get("/protected/dashboard")
def get_dashboard(current_user: UserProfileResponse = Depends(get_current_user)):
    return {
        "status": "access_granted",
        "user_id": current_user.id,
        "active_session": True,
        "metrics": {"total_views": 1024, "data_processed": "12.4 MB"}
    }


@router.get("/admin/metrics")
def get_admin_metrics(admin_user: UserProfileResponse = Depends(require_admin_role)):
    """Stretch Goal: Role-Based Access Control Endpoint (403 vs 401 demonstration)."""
    return {
        "status": "system_nominal",
        "system_load": "0.14",
        "auth_events_24h": 412
    }