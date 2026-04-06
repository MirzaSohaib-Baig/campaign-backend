from fastapi import APIRouter, Depends, Request
from app.core.exceptions import InvalidOperationError
from app.core.security import JWTBearer
from app.helpers import messages
from app.routers.responses import (
    client_side_error,
    internal_server_error,
    send_data_with_info,
)
from app.schemas.campaign_schema import CampaignSchema, UpdateCampaignSchema
from app.services.campaign_service import CampaignService

router = APIRouter(
    prefix="/campaign",
    tags=["campaign routes"],
)

@router.get("s/", dependencies=[Depends(JWTBearer())])
def get_all_campaigns(request: Request, page_number: int = 1, page_limit: int = 10, client: str = None, user_id: str = None, campaign_service: CampaignService = Depends()):
    try:
        data = campaign_service.get_all_campaigns(page_number=page_number, page_limit=page_limit, client=client, user_id=user_id)
        total_count = campaign_service.get_campaign_count()
        return send_data_with_info(
            info=messages.ITEMS_FETCHED + "campaigns",
            data=data,
            total_count=total_count
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.ITEMS_FETCHED_FAILED + "campaigns",
            error=str(e),
        )
        
@router.get("/", dependencies=[Depends(JWTBearer())])
def get_campaign_by_id(campaign_id: str, request: Request, campaign_service: CampaignService = Depends()):
    try:
        data = campaign_service.get_campaign_by_id(campaign_id=campaign_id)
        return send_data_with_info(
            info=messages.ITEM_FETCHED + "campaign",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.ITEM_FETCHED_FAILED + "campaign",
            error=str(e),
        )
        
@router.post("/", dependencies=[Depends(JWTBearer())])
def create_campaign(payload: CampaignSchema, request: Request, campaign_service: CampaignService = Depends()):
    try:
        data = campaign_service.create_campaign(payload=payload)
        return send_data_with_info(
            info=messages.CREATE_SUCCESS + "campaign",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.CREATE_FAILED + "campaign",
            error=str(e),
        )
        
@router.patch("/", dependencies=[Depends(JWTBearer())])
async def update_campaign(payload: UpdateCampaignSchema, request: Request, campaign_service: CampaignService = Depends()):
    try:
        data = await campaign_service.update_campaign(payload=payload)
        return send_data_with_info(
            info=messages.UPDATE_SUCCESS + "campaign",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        print(e)
        return internal_server_error(
            user_msg=messages.UPDATE_FAILED + "campaign",
            error=str(e),
        )
        
@router.delete("/", dependencies=[Depends(JWTBearer())])
def delete_campaign(campaign_id: str, request: Request, campaign_service: CampaignService = Depends()):
    try:
        data = campaign_service.delete_campaign(campaign_id=campaign_id)
        return send_data_with_info(
            info=messages.DELETE_SUCCESS + "campaign",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.DELETE_FAILED + "campaign",
            error=str(e),
        )