from fastapi import Depends
from fastapi.routing import APIRouter, Request
from log.logger import logger
from services import service_provider 
from services.rag_service import RagService
from fastapi import HTTPException 
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates  
from config.constants import FILES_DIR
import os

templates = Jinja2Templates(directory="templates")

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
# def process(files: list[UploadFile]):
async def process(
    request: Request,
    rag_service: RagService = Depends(service_provider.rag_service),
    ):
    try:
        form = await request.form()
        fnames = [] 
        for field in form:
            elem = form[field]
            if isinstance(elem, UploadFile):
                filename = os.path.join(FILES_DIR, elem.filename)  
                content = elem.file.read() 
                with open(filename, 'wb') as f:
                    f.write(content)
                fnames.append(filename)  
        # TODO #doc_id = await rag_service.add_docs(fnames)            
    except Exception as e:
        err = str(e)
        logger.error(f"Error occured while uploading document: {err}")
        raise HTTPException(
        status_code=500,
        detail=err,
        ) 
    return JSONResponse(status_code=200, content={"success": fnames}) 
     