from fastapi import APIRouter, Depends, Response, Request
from app.core.exceptions import AuthError, InvalidOperationError
from app.core.security import JWTBearer
from app.helpers import messages
from app.routers.responses import (
    client_side_error,
    internal_server_error,
    send_data_with_info,
)
from app.schemas.user_auth_schema import ChangePassword, Login, SignUp, UpdateUser
from app.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["user authentication"],
)

@router.post("/signup")
def user_sign_up(payload: SignUp, user_service: UserService = Depends()):
    try:
        data = user_service.create_user(payload=payload)
        return send_data_with_info(
            info=messages.CREATE_SUCCESS + "user",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.CREATE_FAILED + "user",
            error=str(e),
        )


@router.post("/login")
def user_login(payload: Login, response: Response, user_service: UserService = Depends()):
    try:
        data = user_service.login_user(payload=payload)

        tokens = data["tokens"]

        if payload.keepSignedIn:
            response.set_cookie(
                key="refresh_token",
                value=tokens["refresh_token"],
                httponly=True,
                secure=True,
                samesite="lax",
                expires=tokens["refresh_expires_in"]
            )
        return send_data_with_info(
            info=messages.LOGIN_SUCCESS,
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.LOGIN_FAILED,
            error=str(e),
        )

@router.post("/logout")
def user_logout( request: Request, response: Response, user_service: UserService = Depends()):
    try:
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            user_service.logout(refresh_token=refresh_token)
        response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")
        return send_data_with_info(
            info=messages.LOGOUT_SUCCESS,
            data={},
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.LOGOUT_FAILED,
            error=str(e),
        )

@router.post("/refresh")
def refresh_token(request: Request, response: Response, user_service: UserService = Depends()):
    try:
        refresh_token_cookie = request.cookies.get("refresh_token")

        if not refresh_token_cookie:
            raise AuthError("Refresh token is missing or does not match the cookie.")
        
        data = user_service.refresh(refresh_token=refresh_token_cookie)

        response.set_cookie(
            key="refresh_token",
            value=data["new_refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            expires=data["new_refresh_expires_in"]
        )
        return send_data_with_info(
            info=messages.TOKEN_REFRESH_SUCCESS,
            data=data,
        )
    except AuthError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.TOKEN_REFRESH_FAILED,
            error=str(e),
        )
    
@router.post("/", dependencies=[Depends(JWTBearer())])
def change_user_password(payload: ChangePassword, user_service: UserService = Depends()):
    try:

        # Call the service method to change the password
        result = user_service.change_password(
            current_password=payload.current_password,
            new_password=payload.new_password,
            user_id=payload.user_id
        )

        return send_data_with_info(
            info="Password changed successfully.",
            data=result,
        )
    except InvalidOperationError as e:
        return client_side_error(user_msg=str(e))
    except Exception as e:
        return internal_server_error(
            user_msg="Failed to change password",
            error=str(e),
        )

@router.get("/", dependencies=[Depends(JWTBearer())])
def user_profile(user_id: str, user_service: UserService = Depends()):
    try:
        data = user_service.get_user_info(user_id=user_id)
        return send_data_with_info(
            info=messages.ITEM_FETCHED + "user",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.ITEM_FETCHED_FAILED + "user",
            error=str(e),
        )

@router.delete("/", dependencies=[Depends(JWTBearer())])
def delete_user(user_id: str, user_service: UserService = Depends()):
    try:
        data = user_service.delete_user(user_id=user_id)
        return send_data_with_info(
            info=messages.DELETE_SUCCESS + "user",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.DELETE_FAILED + "user",
            error=str(e),
        )

@router.patch("/", dependencies=[Depends(JWTBearer())])
def update_user(payload: UpdateUser, user_service: UserService = Depends()):
    try:
        data = user_service.update_user(payload=payload)
        return send_data_with_info(
            info=messages.UPDATE_SUCCESS + "user",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.UPDATE_FAILED + "user",
            error=str(e),
        )

# @router.post("/logout")
# def user_logout(response: Response):
#     response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")
#     response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")
#     return send_data_with_info(
#         info=messages.LOGOUT_SUCCESS,
#         data={},
#     )