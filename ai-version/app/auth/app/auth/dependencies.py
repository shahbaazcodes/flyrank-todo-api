from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.config import get_supabase_client
from app.auth.schemas import UserProfileResponse

# Enables the "Authorize" padlock button in Swagger UI (/docs)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    supabase: Client = Depends(get_supabase_client)
) -> UserProfileResponse:
    """
    Reusable Guard Dependency: Extracts & verifies the Bearer JWT with Supabase.
    Throws HTTP 401 for missing, malformed, or expired tokens.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    try:
        # Network call to Supabase IdP to verify token integrity and expiration
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = user_response.user
        
        # Extract role from metadata if available (defaults to 'user')
        app_metadata = getattr(user, "app_metadata", {}) or {}
        role = app_metadata.get("role", "user")

        return UserProfileResponse(
            id=str(user.id),
            email=str(user.email),
            created_at=str(user.created_at),
            role=role,
            user_metadata=getattr(user, "user_metadata", {}) or {}
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def require_admin_role(
    current_user: UserProfileResponse = Depends(get_current_user)
) -> UserProfileResponse:
    """
    RBAC Authorization Guard (Stretch): Differentiates AuthN (401) from AuthZ (403).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required"
        )
    return current_user