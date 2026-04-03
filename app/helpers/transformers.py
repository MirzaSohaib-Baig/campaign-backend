from app.models.users import User
from app.models.campaigns import Campaign

def transform_user(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "bio": user.bio,
        "country": user.country,
        "city": user.city,
        "facebook_link": user.facebook_link,
        "x_link": user.x_link,
        "linkedin_link": user.linkedin_link,
        "instagram_link": user.instagram_link,
        "phone_number": user.phone_number,
        "created_at": user.created_at,
    }

def transform_campaign(campaign: Campaign):
    return {
        "id": campaign.id,
        "name": campaign.name,
        "client": campaign.client,
        "channel": campaign.channel,
        "status": campaign.status,
        "impressions": campaign.impressions,
        "clicks": campaign.clicks,
        "conversions": campaign.conversions,
        "spend": campaign.spend,
        "budget": campaign.budget,
        "revenue": campaign.revenue,
        "ctr": round((campaign.clicks / campaign.impressions) * 100, 2) if campaign.impressions > 0 else 0.0,
        "roas": round(campaign.revenue / campaign.spend, 2) if campaign.spend > 0 else 0.0,
        "user_id": campaign.user_id,
        "created_at": campaign.created_at
    }