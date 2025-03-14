# routes to /chat


'''
   def init_chatbot(self):
        """
        Build 'Chatbot' assistant
        """

        self.load_and_split_docs()
        self.configure_retriever()
        self.configure_llm()
        self.create_chain()


'''   


'''
Chatbot MAIN

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import time
import contextlib
import threading
from datetime import datetime
from chatbot import TxtChatBot

# Create a FastAPI app
app = FastAPI()
chatbot = TxtChatBot()
chatbot.init_chatbot()


# Create a class for the input data
class InputData(BaseModel):
    question: str


# Create a class for the output data
class OutputData(BaseModel):
    answer: str


@app.get("/")
async def root():
    return OutputData(answer="Hello World!")


# Create a 'chat' route for the web application
@app.post("/chat", response_model=OutputData)
async def chat(request: InputData):
    try:
        answer = chatbot.generate_response(request.question)
        return OutputData(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# https://github.com/fastapi/fastapi/discussions/7457
class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    # https://docs.python.org/3/library/contextlib.html
    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


def main():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = Server(config=config)

    with server.run_in_thread():
        # Server started.

        print("Hello! I am a chatbot. I can answer questions based on the content of a your documents.")

        while True:
            current_datetime = datetime.now()
            user_input = input("Do you have any questions? To exit, type 'bye': ")

            # response = requests.get(f"http://localhost:8000/")
            response = requests.post("http://localhost:8000/chat", json={'question': user_input})
            answer = response.json()  # ['answer']
            elapsed_time = datetime.now() - current_datetime

            print("TxtChatbot answer: ", answer)
            print("Time elapsed: ", elapsed_time.total_seconds(), "seconds")

            if user_input.lower() == "bye":
                break

        # Server stopped. 
'''