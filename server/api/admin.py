
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.config import ADMIN_USER_USERNAME
from server.lib.AuthUtils import AuthUtils
from server.models.database import UserRecord, get_async_session

from .auth import LoginRequest, TokenResponse

router = APIRouter()


@router.post(
    "/login",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid username or password"},
        500: {"description": "Internal server error"},
    }
)
async def login(
    req: LoginRequest, 
    response: Response,
    db_client: AsyncSession = Depends(get_async_session)
) -> TokenResponse:
    """Login user and return JWT tokens"""
    try:
        # find user
        result = None
        if req.type == "email":
            result = await db_client.execute(
                select(UserRecord).where(UserRecord.email == req.identifier)
            )
        elif req.type == "username":  # username
            result = await db_client.execute(
                select(UserRecord).where(UserRecord.username == req.identifier)
            )
        else:
            assert False, "Unreachable"
        user = result.first()

        if user is None or not AuthUtils.verify_password(
            req.password, user[0].hashed_password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        if user[0].username != ADMIN_USER_USERNAME:
            raise HTTPException(
                status_code=401,
                detail="Only admin user can login"
            )

        # generate tokens
        access_token = AuthUtils.create_access_token({"sub": user[0].id})
        refresh_token = AuthUtils.create_refresh_token({"sub": user[0].id})

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/api/auth"
        )

        return TokenResponse(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/refresh",
    responses = {
        200: {"description": "Access token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
        500: {"description": "Internal server error"},
    })
async def refresh_access_token(
    request: Request,
    db_client: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Use Refresh Token to get a new Access Token if access token expired"""
    # get Refresh Token from cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    try:
        # verify Refresh Token
        payload = AuthUtils.verify_token(refresh_token)

        # ensure it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401, detail="Invalid token type"
            )

        user_id_str = payload.get("sub")

        # convert user_id from string to integer
        try:
            user_id = int(user_id_str) # type: ignore
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=401,
                detail="Invalid user ID in token"
            )

        # verify user still exists
        user = await db_client.get(UserRecord, user_id)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )
        elif user.username != ADMIN_USER_USERNAME: # type: ignore
            raise HTTPException(
                status_code=401,
                detail="Only admin user can refresh access token by this method"
            )

        # create Access Token
        new_access_token = AuthUtils.create_access_token({"sub": user_id})

        return TokenResponse(access_token=new_access_token)

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid refresh token"
        )
    except Exception as e:
        logger.exception(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/logout",
    responses={
        200: {"description": "Logged out successfully"}
    }
)
async def logout(response: Response) -> dict[str, str]:
    """Logout user by clearing the Refresh Token"""
    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"message": "Logged out successfully"}
