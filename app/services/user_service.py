from app.core.exceptions import NotFoundError
from app.core.security import generate_access_token, verify_password, hash_password, generate_refresh_token, decode_token
from app.helpers import messages
from app.helpers.transformers import transform_user
from app.repository.users_repository import UserRepository
from app.repository.refresh_tokens_repository import RefreshTokenRepository
from app.services.base_service import BaseService
from fastapi import Depends
from app.core.exceptions import AuthError
import datetime as maintime
from datetime import datetime

class UserService(BaseService):
    def __init__(self, repository: UserRepository = Depends(UserRepository), refresh_token_repository: RefreshTokenRepository = Depends(RefreshTokenRepository)):
        super().__init__(repository)
        self.repository = repository
        self.refresh_token_repository = refresh_token_repository

    def create_user(self, payload):
        existing_user = self.repository.get_user_by_username(payload.username)
        if existing_user:
            raise Exception(messages.ALREADY_EXISTS + "username")
        user = self.repository.create_user(payload)
        return transform_user(user)

    def login_user(self, payload):
        user = self.repository.get_user_by_username(payload.username)

        if not user:
            raise Exception(messages.NOT_FOUND + "user")

        if not verify_password(payload.password, user.password):
            raise Exception(messages.INVALID_CREDENTIALS)

        user = transform_user(user)

        access_token, access_exp = generate_access_token(user)

        response = {
            "user": user,
            "tokens": {
                "access_token": access_token,
                "access_expires_in": access_exp,
            },
            "keepSignedIn": payload.keepSignedIn
        }

        # ✅ Only create refresh token if keepSignedIn is TRUE
        if payload.keepSignedIn:
            refresh_token, refresh_exp = generate_refresh_token(user)

            self.refresh_token_repository.create_refresh_token(user_id=user["id"], token=refresh_token, expires_at=refresh_exp)

            response["tokens"]["refresh_token"] = refresh_token
            response["tokens"]["refresh_expires_in"] = refresh_exp

        return response
    def refresh(self, refresh_token: str):
        stored_token = self.refresh_token_repository.get_refresh_token(refresh_token)

        if not stored_token:
            raise AuthError("Refresh token is invalid or revoked.")
        
        if stored_token.expires_at < datetime.now(maintime.timezone.utc):
            raise AuthError("Refresh token has expired.")
        
        payload = decode_token(refresh_token)

        if payload["type"] != "refresh":
            raise AuthError("Invalid token type.")

        user_id = payload["id"]

        self.refresh_token_repository.revoke_refresh_token(refresh_token)

        new_access_token, new_access_token_expires = generate_access_token({"id": user_id})
        new_refresh_token, refresh_token_expires = generate_refresh_token({"id": user_id})

        self.refresh_token_repository.create_refresh_token({
            "user_id": user_id,
            "token": new_refresh_token,
            "expires_at": refresh_token_expires
        })

        return {"new_access_token": new_access_token, "new_access_expires_in": new_access_token_expires, "new_refresh_token": new_refresh_token, "new_refresh_expires_in": refresh_token_expires}
    
    def logout(self, refresh_token: str):
        self.refresh_token_repository.revoke_refresh_token(refresh_token)

    def change_password(self, current_password: str, new_password: str, user_id: str):

        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(messages.NOT_FOUND + "user")

        # Verify the current password
        if not verify_password(current_password, user.password):
            raise Exception(messages.INVALID_CREDENTIALS + "current password is incorrect.")

        # Hash the new password
        hashed_new_password = hash_password(new_password)

        # Update the user's password in the database
        self.repository.update_user_password(user_id=user_id, new_password=hashed_new_password)

        return {"message": "Password updated successfully"}
    
    def get_user_info(self, user_id):
        user = self.repository.get_user_by_id(user_id)
        return transform_user(user)

    def delete_user(self, user_id):
        return self.repository.delete_user(user_id)

    def update_user(self, payload):
        user = self.repository.get_user_by_id(payload.user_id)
        if not user:
            raise Exception(messages.NOT_FOUND + "user")
        updated_user = self.repository.update_user(payload.user_id, payload)
        return transform_user(updated_user)
