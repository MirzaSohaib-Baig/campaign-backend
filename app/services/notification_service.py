# app/services/notification_service.py
from fastapi import Depends
from app.repository.notifications_repository import NotificationRepository
from app.repository.alert_rule_repository import AlertRuleRepository
from app.core.alert_engine import evaluate_campaign
from app.helpers.transformers import transform_notification, transform_alert_rule
from app.core.websocket_manager import ws_manager

class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRepository = Depends(),
        alert_rule_repo:   AlertRuleRepository    = Depends(),
    ) -> None:
        self.notification_repo = notification_repo
        self.alert_rule_repo   = alert_rule_repo

    async def check_and_notify(self, campaign):
        rules = self.alert_rule_repo.get_rules_for_campaign(campaign.get("id"))
        # print("Rules for campaign", rules)
        triggered = evaluate_campaign(campaign, rules)
        # print("Triggered", triggered)
        for alert in triggered:
            # print("Saving notification", alert)
            notification = self.notification_repo.save_notification(alert)
            # print("Saved notification", notification.id)
            await ws_manager.send_to_user(
                alert["user_id"],
                {
                    "id":          str(notification.id),
                    "type":        alert["alert_type"],
                    "message":     alert["message"],
                    "campaign_id": alert["campaign_id"],
                    "is_read":     False,
                    "created_at":  notification.created_at.isoformat(),
                }
            )

    def get_notifications(self, user_id: str, unread_only: bool = False):
        return self.notification_repo.get_user_notifications(user_id, unread_only)

    def mark_all_read(self, user_id: str):
        self.notification_repo.mark_all_read(user_id)

    def mark_one_read(self, notification_id: str):
        self.notification_repo.mark_one_read(notification_id)

    def get_unread_count(self, user_id: str):
        return self.notification_repo.get_unread_count(user_id)

    def create_rule(self, data):
        rule = self.alert_rule_repo.create_rule(data)
        return transform_alert_rule(rule)

    def get_rules_for_user(self, user_id: str):
        return self.alert_rule_repo.get_rules_for_user(user_id)

    def delete_rule(self, rule_id: str):
        return self.alert_rule_repo.delete_rule(rule_id)

    def toggle_rule(self, rule_id: str, payload):
        toggle_rule = self.alert_rule_repo.toggle_rule(rule_id, payload)
        return transform_alert_rule(toggle_rule)