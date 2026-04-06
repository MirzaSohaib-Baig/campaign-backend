# app/routers/notification_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.websocket_manager import ws_manager
from app.core.security import JWTBearer
from app.services.notification_service import NotificationService
from app.schemas.notification_schema import NotificationSchema, AlertRuleSchema, UpdateAlertRuleSchema
from app.core.exceptions import InvalidOperationError
from app.routers.responses import send_data_with_info, client_side_error, internal_server_error
from app.helpers import messages

router = APIRouter(
    prefix="/notification",
    tags=["notifications"],
)

# ── WebSocket ──────────────────────────────────────────────────────────────────

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    user_id: str,
    websocket: WebSocket,
):
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)

# ── Notifications ──────────────────────────────────────────────────────────────

@router.get("s/", dependencies=[Depends(JWTBearer())])
def get_notifications(
    user_id: str,
    unread_only: bool = False,
    service: NotificationService = Depends(),
):
    try:
        data = service.get_notifications(user_id=user_id, unread_only=unread_only)
        return send_data_with_info(
            info=messages.ITEM_FETCHED + "notifications",
            data=data,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.ITEM_FETCHED_FAILED + "notifications",
            error=str(e),
        )

@router.get("/unread-count", dependencies=[Depends(JWTBearer())])
def get_unread_count(
    user_id: str,
    service: NotificationService = Depends(),
):
    try:
        count = service.get_unread_count(user_id=user_id)
        return send_data_with_info(
            info=messages.ITEM_FETCHED + "unread count",
            data={"count": count},
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.ITEM_FETCHED_FAILED + "unread count",
            error=str(e),
        )

@router.patch("s/read", dependencies=[Depends(JWTBearer())])
def mark_all_read(
    user_id: str,
    service: NotificationService = Depends(),
):
    try:
        service.mark_all_read(user_id=user_id)
        return send_data_with_info(
            info="All notifications marked as read",
            data={},
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg="Failed to mark notifications as read",
            error=str(e),
        )

@router.patch("/read", dependencies=[Depends(JWTBearer())])
def mark_one_read(
    notification_id: str,
    service: NotificationService = Depends(),
):
    try:
        service.mark_one_read(notification_id=notification_id)
        return send_data_with_info(
            info="Notification marked as read",
            data={},
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg="Failed to mark notification as read",
            error=str(e),
        )

# ── Alert Rules ────────────────────────────────────────────────────────────────

@router.post("/rule", dependencies=[Depends(JWTBearer())])
def create_rule(
    payload: AlertRuleSchema,
    service: NotificationService = Depends(),
):
    try:
        rule = service.create_rule(data=payload)
        return send_data_with_info(
            info=messages.CREATE_SUCCESS + "alert rule",
            data=rule,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.CREATE_FAILED + "alert rule",
            error=str(e),
        )

@router.get("/rules", dependencies=[Depends(JWTBearer())])
def get_rules(
    user_id: str,
    service: NotificationService = Depends(),
):
    try:
        rules = service.get_rules_for_user(user_id=user_id)
        return send_data_with_info(
            info=messages.ITEM_FETCHED + "alert rules",
            data=rules,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.ITEM_FETCHED_FAILED + "alert rules",
            error=str(e),
        )

@router.delete("/rule", dependencies=[Depends(JWTBearer())])
def delete_rule(
    rule_id: str,
    service: NotificationService = Depends(),
):
    try:
        service.delete_rule(rule_id=rule_id)
        return send_data_with_info(
            info=messages.DELETE_SUCCESS + "alert rule",
            data={},
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.DELETE_FAILED + "alert rule",
            error=str(e),
        )

@router.patch("/rule/toggle", dependencies=[Depends(JWTBearer())])
def toggle_rule(
    payload: UpdateAlertRuleSchema,
    service: NotificationService = Depends(),
):
    try:
        rule = service.toggle_rule(rule_id=payload.rule_id, payload=payload)
        return send_data_with_info(
            info=messages.UPDATE_SUCCESS + "alert rule",
            data=rule,
        )
    except InvalidOperationError as e:
        return client_side_error(
            user_msg=str(e),
        )
    except Exception as e:
        return internal_server_error(
            user_msg=messages.UPDATE_FAILED + "alert rule",
            error=str(e),
        )