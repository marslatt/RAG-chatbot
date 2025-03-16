from fastapi import Depends
from fastapi.routing import APIRouter, Request
from log.logger import logger
from services import service_provider 
from services.rag_service import RagService 
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile
from fastapi.responses import HTMLResponse 
from config.constants import FILES_DIR
from templates import templates
import os

rag_router = APIRouter()  
  
@rag_router.get("/upload", response_class=HTMLResponse)
async def upload( 
    request: Request, 
    ) -> HTMLResponse: 
    return templates.TemplateResponse(
        request=request, 
        name="upload.html",  
    )  

@rag_router.post("/process") 
async def process(
    request: Request,
    rag_service: RagService = Depends(service_provider.rag_service),
    ) -> JSONResponse:
    try:
        form = await request.form() 
        for field in form:
            elem = form[field]
            if isinstance(elem, UploadFile):
                filename = os.path.join(FILES_DIR, elem.filename)  
                content = elem.file.read() 
                with open(filename, 'wb') as f:
                    f.write(content)   
        doc_ids = await rag_service.add_docs()            
    except Exception as e:
        err = str(e)
        logger.error(f"Error occured while uploading document: {err}")
        return JSONResponse(status_code=500, content={"error": err})  
    
    return JSONResponse(status_code=200, content={"success": doc_ids}) 
     