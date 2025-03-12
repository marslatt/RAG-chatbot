from pydantic import BaseModel 

# TODO 

class BaseDataRequest(BaseModel):
    data: str
  
class BaseDataResponse(BaseModel):
    data: str