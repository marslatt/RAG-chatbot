from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import uvicorn

from chatbot import TxtChatBot

# Create a FastAPI app
app = FastAPI()


# Create a class for the input data
class InputData(BaseModel):
    question: str
    # context: str


# Create a class for the output data
class OutputData(BaseModel):
    answer: str


chatbot = TxtChatBot()
chatbot.init_chatbot()


# Create a route for the web application
@app.post("/chat", response_model=OutputData)
async def chat(request: InputData):
    try:
        answer = chatbot.generate_response(request.question)
        return OutputData(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
