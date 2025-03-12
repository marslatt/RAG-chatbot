from schema import BaseDataResponse, BaseDataRequest 
from fastapi import Depends
from fastapi.routing import APIRouter, Request
from log.logger import logger
from services import service_provider 
from services.rag_service import RagService
from fastapi import HTTPException 
from fastapi import File, UploadFile

data_router = APIRouter() 
 
# TODO injecting global dependency for RagService as such is already configured during app init
@data_router.get("/data", response_model=BaseDataResponse)
async def add_data( 
    request: Request, # BaseDataRequest,
    rag_service: RagService = Depends(service_provider.RagService),
    ) -> BaseDataResponse:
    try:
        response = await rag_service.add_docs() 
    except Exception as e: 
            err = f"Request cannot be completed: {str(e)}"
            logger.error(err)
            raise HTTPException(
            status_code=500,
            detail=err,
        )  
    return BaseDataResponse(data=response) 

'''
@data_router.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception as e:
        err = str(e)
        logger.error(f"Error occured while uploading documents: {err}")
        raise HTTPException(
            status_code=500,
            detail=err,
        )  
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}
'''