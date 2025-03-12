from fastapi import APIRouter, Request 
from log import logger
from fastapi import HTTPException 
from schema import BaseResponse 

ping_router = APIRouter() 
 
@ping_router.get(path="/ping", response_model=BaseResponse)
async def ping(
    request: Request 
) -> BaseResponse:
    try:
        response = f"{request.app.title} - v.{request.app.version}" 
    except Exception as e: 
            err = f"Request cannot be completed: {str(e)}"
            logger.error(err)
            raise HTTPException(
            status_code=500,
            detail=err,
        )  
    return BaseResponse(data=response) 