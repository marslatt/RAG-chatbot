from pydantic import BaseModel 

class BaseRequest(BaseModel):
    data: str
  
class BaseResponse(BaseModel):
    data: str