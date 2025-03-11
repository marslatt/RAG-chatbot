from fastapi import APIRouter, Request 
from log import logger
from fastapi import HTTPException 
from data import BaseOutputData 

ping_router = APIRouter() 
 
@ping_router.get(path="/ping", response_model=BaseOutputData)
async def ping(
    request: Request 
) -> BaseOutputData:
    try:
        response = f"{request.app.title} - v.{request.app.version}" 
    except Exception as e: 
            logger.error(e.message)
            raise HTTPException(
            status_code=500,
            detail=e.message,
        )  
    return BaseOutputData(data=response) 