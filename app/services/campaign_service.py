from app.core.exceptions import NotFoundError
from app.helpers import messages
from app.helpers.transformers import transform_campaign
from app.repository.campaigns_repository import CampaignRepository
from app.services.base_service import BaseService
from app.services.notification_service import NotificationService
from app.repository.notifications_repository import NotificationRepository
from app.repository.alert_rule_repository import AlertRuleRepository
from fastapi import Depends

class CampaignService(BaseService):
    def __init__(self, repository: CampaignRepository = Depends(CampaignRepository)):
        super().__init__(repository)
        self.repository = repository
        
    def create_campaign(self, payload):
        payload.name = payload.name.strip()
        payload.client = payload.client.strip()
        payload.channel = payload.channel.strip()
        campaign = self.repository.create_campaign(payload)
        return transform_campaign(campaign)

    def get_campaign_by_id(self, campaign_id):
        campaign = self.repository.get_campaign_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(messages.NOT_FOUND + "campaign")
        return transform_campaign(campaign)
    
    def get_all_campaigns(self, page_number, page_limit, client=None):
        return self.repository.get_all_campaigns(page_number=page_number, page_limit=page_limit, client=client)
    
    def get_campaign_count(self):
        return self.repository.get_campaign_count()
    
    def delete_campaign(self, campaign_id):
        return self.repository.delete_campaign(campaign_id=campaign_id)
    
    async def update_campaign(self, payload):
        campaign = self.repository.get_campaign_by_id(payload.campaign_id)
        if not campaign:
            raise NotFoundError(messages.NOT_FOUND + "campaign")
        payload.name = payload.name.strip() if payload.name else campaign.name
        payload.client = payload.client.strip() if payload.client else campaign.client
        payload.channel = payload.channel.strip() if payload.channel else campaign.channel
        updated_campaign = self.repository.update_campaign(campaign_id=payload.campaign_id, schema=payload)

        notification_service = NotificationService(
            notification_repo=NotificationRepository(db=self.repository.db),
            alert_rule_repo=AlertRuleRepository(db=self.repository.db),
        )
        await notification_service.check_and_notify(transform_campaign(updated_campaign))
        return transform_campaign(updated_campaign)