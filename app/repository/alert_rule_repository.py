from sqlalchemy.orm import Session
from fastapi import Depends
from app.config.database_config import get_db
from app.models.notification_models import AlertRule
from app.repository.base_repository import BaseRepository
from app.schemas.notification_schema import AlertRuleSchema, UpdateAlertRuleSchema
from app.helpers.transformers import transform_alert_rule

class AlertRuleRepository(BaseRepository):
    def __init__(self, db: Session = Depends(get_db)) -> None:
        super().__init__(AlertRule, db)

    def create_rule(self, schema) -> AlertRule:
        alert_rule = AlertRuleSchema(**schema.dict())
        return self.create(alert_rule)

    def get_rules_for_campaign(self, campaign_id: str) -> list:
        rules = self.read_where(campaign_id=campaign_id, is_active=True)
        return [transform_alert_rule(rule) for rule in rules]

    def get_rules_for_user(self, user_id: str) -> list:
        rules = self.read_where(user_id=user_id)
        return [transform_alert_rule(rule) for rule in rules]

    def delete_rule(self, rule_id: str) -> None:
        return self.delete(id=rule_id)

    def toggle_rule(self, rule_id: str, schema) -> AlertRule:
        toggle_rule = UpdateAlertRuleSchema(**schema.dict(exclude_unset=True))
        return self.update(id=rule_id, schema=toggle_rule)