from sqlalchemy.orm import Session
from app.config.database_config import get_db
from app.models.refresh_tokens import RefreshToken
from app.repository.base_repository import BaseRepository
from fastapi import Depends

class RefreshTokenRepository(BaseRepository):
    def __init__(self, db: Session = Depends(get_db)) -> None:
        super().__init__(RefreshToken, db)

    def create_refresh_token(self, user_id: str, token: str, expires_at):
        db_token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_refresh_token(self, token: str):
        return self.db.query(self.model).filter(self.model.token == token, self.model.is_revoked == False).first()

    def revoke_refresh_token(self, token: str):
        self.db.query(self.model).filter(self.model.token == token).update({"is_revoked": True})
        self.db.commit()
    
    def revoke_all_tokens_for_user(self, user_id: str):
        self.db.query(self.model).filter(self.model.user_id == user_id, self.model.is_revoked == False).update({"is_revoked": True})
        self.db.commit()