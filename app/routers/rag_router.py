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
                logger.info(f"{filename} uploaded successfully.")    
        doc_ids = await rag_service.add_docs()  
        logger.info(f"{filename} added to Chroma db successfully.")            
    except Exception as e:
        err = f"Error occured while uploading document: {str(e)}"
        logger.error(err)
        return JSONResponse(status_code=422, content={"error": err})  # 422 Unprocessable Content
    
    return JSONResponse(status_code=200, content={"success": doc_ids}) 
     