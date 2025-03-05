'''
from fastapi import status
from fastapi import Response
from fastapi import Depends
from fastapi.routing import APIRouter
from log.logger import logger
from services import service_provider 
from services.some_service import SomeService
   
 
@app.post("/some-query", response_model=BaseOutputData)
async def query(
    request: BaseInputData
    some_service: SomeService = Depends(service_provider.some_service),):
    try:
        response = await some_service.generate_response(request.data)
        return OutputData(data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''