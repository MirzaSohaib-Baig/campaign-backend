from app.routers.user_authentication import router as user_authentication_router
from app.routers.campaign_routes import router as campaign_router

V1_ROUTES = [user_authentication_router]
V2_ROUTES = [campaign_router]