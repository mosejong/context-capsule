from fastapi import Request

from src.utils.logger import log_request


async def request_logger(request: Request, call_next):
    log_request(method=request.method, path=request.url.path)
    return await call_next(request)
