from sqlalchemy.orm import Session
from app.config.database_config import get_db
from app.models.campaigns import Campaign
from app.repository.base_repository import BaseRepository
from app.schemas.campaign_schema import CampaignSchema, UpdateCampaignSchema
from app.helpers.transformers import transform_campaign
from fastapi import Depends

class CampaignRepository(BaseRepository):
    def __init__(self, db: Session = Depends(get_db)) -> None:
        super().__init__(Campaign, db)

    def create_campaign(self, schema):
        details = CampaignSchema(**schema.dict())
        return self.create(details)

    def get_campaign_by_id(self, id):
        return self.read_one(id)

    def get_all_campaigns(self, page_number, page_limit, client=None):
        campaigns = self.read_all(page=page_number, limit=page_limit, client=client)
        return [transform_campaign(campaign) for campaign in campaigns]

    def get_campaign_count(self):
        return self.db.query(self.model).count()

    def delete_campaign(self, campaign_id: str):
        return self.delete(id=campaign_id)

    def update_campaign(self, campaign_id: str, schema):
        update_campaign = UpdateCampaignSchema(**schema.dict(exclude_unset=True))
        return self.update(id=campaign_id, schema=update_campaign)
