from fastapi import APIRouter  
from log.logger import logger
from fastapi import HTTPException 
from data.base_data import BaseOutputData, BaseInputData 

ping_router = APIRouter()
 
@ping_router.get(path="/ping", response_model=BaseOutputData)
async def ping(
    request: BaseInputData 
) -> BaseOutputData:
    try:
        response = f"[{request.app.title}] - [{request.app.version}]" 
    except Exception as e: 
            logger.error(e.message)
            raise HTTPException(
            status_code=500,
            detail=e.message,
        )  
    return BaseOutputData(data=response) 