from fastapi import Header, HTTPException, status
from firebase_admin import auth
from firebase_admin.auth import InvalidIdTokenError

def get_current_user_id(authorization: str = Header(None)) -> str:
    """Verifies Firebase ID Token and returns the authenticated user's UID."""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing."
        )

    # Header is expected to be "Bearer <token>"
    try:
        scheme, id_token = authorization.split()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Must be 'Bearer <token>'."
        )

    if scheme.lower() != 'bearer':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication scheme must be Bearer."
        )

    try:
        # Core verification using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
        
    except InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server could not process token verification."
        )