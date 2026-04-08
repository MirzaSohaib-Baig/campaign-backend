from sqlalchemy.orm import Session
from fastapi import Depends
from app.config.database_config import get_db
from app.models.notification_models import Notification
from app.repository.base_repository import BaseRepository
from app.schemas.notification_schema import NotificationSchema
from app.helpers.transformers import transform_notification

class NotificationRepository(BaseRepository):
    def __init__(self, db: Session = Depends(get_db)) -> None:
        super().__init__(Notification, db)  # ← pass Notification as the model

    def save_notification(self, schema: dict):
        notification = NotificationSchema(**schema)
        return self.create(notification)  # ← reuse base create

    def get_user_notifications(self, user_id: str, unread_only: bool = False):
        query = self.read_where(user_id=user_id, is_read=False)
        if unread_only:
            query = self.read_where(user_id=user_id, is_read=False)
        return [transform_notification(notification) for notification in query]

    def mark_all_read(self, user_id: str):
        query = self.read_where(user_id=user_id, is_read=False)
        for notifications in query:
            notifications.is_read = True
        self.db.commit()

    def mark_one_read(self, notification_id: str):
        notification = self.read_one(id=notification_id)  # ← reuse base read_one
        notification.is_read = True
        self.db.commit()

    def get_unread_count(self, user_id: str):
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.is_read == False)
            .count()
        )
    
    def get_unread_notifications(self, campaign_id: str):
        return self.read_where(campaign_id=campaign_id, is_read=False)