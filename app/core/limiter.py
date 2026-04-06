# app/core/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_real_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host

limiter = Limiter(key_func=get_real_ip if get_real_ip else get_remote_address, default_limits=["100/minute"])