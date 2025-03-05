from pydantic import BaseModel
 
class BaseInputData(BaseModel):
    data: str
 
class BaseOutputData(BaseModel):
    data: str