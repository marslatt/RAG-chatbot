# Import the libraries
# from fastapi import FastAPI, Request
# from transformers import pipeline
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from pydantic import BaseModel

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


# Load a local LLM using Hugging Face Transformers
# Other models for QA: bert-base-cased, distilbert/distilbert-base-uncased, stabilityai/stablelm-zephyr-3b
# qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

chatbot = TxtChatBot()
chatbot.init_chatbot()


# Create a route for the web application
@app.post("/chat", response_model=OutputData)
async def chat(request: InputData):
    try:
        # response = qa_pipeline(question=request.question, context=request.context)
        # return OutputData(answer=response['answer'])
        answer = chatbot.generate_response(request.question)
        return OutputData(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#

'''
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
model = AutoModelForCausalLM.from_pretrained("bert-base-cased")

# ValueError: Cannot use chat template functions because tokenizer.chat_template is not set and no template argument 
# was passed! For information about writing templates and setting the tokenizer.chat_template attribute, please see 
# the documentation at https://huggingface.co/docs/transformers/main/en/chat_templating

@app.post("/generate", response_model=OutputData)
def generate(request: Request, input_data: InputData):
    prompt = [{'role': 'user', 'content': input_data.prompt}]
    inputs = tokenizer.apply_chat_template(prompt, add_generation_prompt=True, return_tensors='pt')
    # prompt_length = inputs[0].shape[0]
    # tokens = model.generate(inputs.to(model.device), max_new_tokens=1024, temperature=0.8, do_sample=True)
    # response = tokenizer.decode(tokens[0][prompt_length:], skip_special_tokens=True)
    response = tokenizer.decode(inputs[0])
    return OutputData(response=response)
'''

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
