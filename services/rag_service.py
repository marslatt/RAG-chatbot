
class RagService:
     pass

'''
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadbx import DocumentSHA256Generator
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from config.constants import FILES_DIR

# https://medium.com/the-modern-scientist/building-generative-ai-applications-using-langchain-and-openai-apis-ee3212400630


class TxtChatBot:

    def __init__(self):
        self.docs = None
        self.retriever = None
        self.llm = None
        self.chain = None
        self.chat_history = []

    def load_and_split_docs(self):
        """
        Load and split documents
        """

        # path to the directory containing .txt documents
        docs_path = "." + os.sep + FILES_DIR

        # load documents
        loader = DirectoryLoader(
            docs_path,
            glob='**/*.txt',
            loader_cls=TextLoader
        )
        raw_documents = loader.load()

        # split documents into chunks
        text_splitter = CharacterTextSplitter(
            separator=".",  # split on a full-stop
            chunk_size=1000,
            chunk_overlap=50  # overlap to avoid loss of information
        )

        self.docs = text_splitter.split_documents(raw_documents)

    def configure_retriever(self):
        """
        Set up Chroma vector database and retriever
        """

        # path to the directory containing .txt documents
        db_path = "." + os.sep + constants.CHROMA_DIR
        cln_name = "doc"

        # Chroma client to save and load the database from the local machine
        # data will be persisted automatically and loaded on start (if it exists)
        client = PersistentClient(path=db_path)

         
        # for cleaner reloading, delete old collection if exists
        #try:
            #client.get_collection(name=cln_name)
            #client.delete_collection(name=cln_name)
        #except Exception as err:
            # logger.logg(err)
            #pass
     

        embedding_func = OpenAIEmbeddingFunction(api_key=constants.OPENAI_API_KEY)

        collection = client.get_or_create_collection(
            name=cln_name,
            embedding_function=embedding_func
        )

        unique_docs = list(set(doc.page_content for doc in self.docs))
        doc_ids = DocumentSHA256Generator(documents=unique_docs)

        try:
            collection.upsert(
                ids=doc_ids,
                documents=unique_docs,
            )
        except Exception as err:
            # logger.logg(err)
            # print(err)
            pass

        embeddings = OpenAIEmbeddings(openai_api_key=constants.OPENAI_API_KEY)

        db = Chroma(
            client=client,
            collection_name=cln_name,
            embedding_function=embeddings,
            persist_directory=db_path,
        )

        # self.retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        self.retriever = db.as_retriever()

    def configure_llm(self):
        """
        Create and configure LLM
        """

        self.llm = ChatOpenAI(
            model=constants.OPENAI_LLM,
            openai_api_key=constants.OPENAI_API_KEY
        )

    def create_chain(self):
        """
        Create conversational history-aware retrieval chain
        """

        # make the output appear as string
        # output_parser = StrOutputParser()

        contextualized_prompt = ChatPromptTemplate.from_messages([
            ("system", "Based on chat history and user question, make the question understandable without history."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create a chain that takes conversation history and returns documents.
        # If there is no chat_history, then the input is just passed directly to the retriever. If there is
        # chat_history, then the prompt and LLM will be used to generate a search query. That search query is
        # then passed to the retriever.
        contextualized_retriever = create_history_aware_retriever(self.llm, self.retriever, contextualized_prompt)

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the user question based on the below context:\\n\\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create a chain for passing a list of Documents to a model.
        # prompt (param) - Prompt used for formatting each document into a string.
        # Returns LCEL Runnable. The input is a dictionary that must have a “context” key that maps to a List[Document],
        # and any other input variables expected in the prompt. The Runnable return type depends on output_parser used.
        document_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        # Create retrieval chain that retrieves documents and then passes them on.
        # retriever (param) – Retriever-like object that returns list of documents.
        # chain (param) – Runnable that takes inputs and produces a string output. The inputs to this will be any
        # original inputs to this chain, a new context key with the retrieved documents, and chat_history (if not
        # present in the inputs) with a value of [] to easily enable conversational retrieval.
        # Returns an LCEL Runnable
        self.chain = create_retrieval_chain(contextualized_retriever, document_chain)

    def init_chatbot(self):
        """
        Build 'Chatbot' assistant
        """

        self.load_and_split_docs()
        self.configure_retriever()
        self.configure_llm()
        self.create_chain()

    def generate_response(self, user_input):
        """
        Perform history-aware QA task
        """

        # TODO check if chatbot was configured properly

        response = self.chain.invoke(
            {
                "chat_history": self.chat_history,
                "input": user_input
            }
        )

        answer = response['answer']
        self.chat_history.append(user_input)
        self.chat_history.append(answer)

        return answer
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
