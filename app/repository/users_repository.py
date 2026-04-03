from sqlalchemy.orm import Session
from app.config.database_config import get_db
from app.core.security import hash_password
from app.models.users import User
from app.repository.base_repository import BaseRepository
from app.schemas.user_auth_schema import SignUp, UpdateUser
from fastapi import Depends

class UserRepository(BaseRepository):
    def __init__(self, db: Session = Depends(get_db)) -> None:
        super().__init__(User, db)

    def create_user(self, schema):
        details = SignUp(**schema.dict())
        details.password = hash_password(details.password)
        return self.create(details)

    def get_user_by_username(self, username):
        return self.db.query(self.model).filter(self.model.username == username).first()

    def get_user_by_id(self, id):
        return self.read_one(id)
    
    def update_user_password(self, user_id: str, new_password: str):
        user = self.get_user_by_id(user_id)
        if not user:
            raise Exception("User not found")
        user.password = new_password
        self.db.commit()
        return user

    def delete_user(self, user_id: str):
        return self.delete(id=user_id)
    
    def update_user(self, user_id: str, schema):
        update_user = UpdateUser(**schema.dict(exclude_unset=True))
        update_user.password = hash_password(update_user.password)
        return self.update(id=user_id, schema=update_user)
