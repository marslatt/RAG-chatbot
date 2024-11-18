from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_openai import ChatOpenAI
# from transformers import AutoModelForCausalLM
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import os
# import torch
import constants


def load_and_split_docs():
    """
    Load and Split Documents
    """

    # path to the directory containing .txt documents
    docs_path = "." + os.sep + "data"

    # load documents
    loader = DirectoryLoader(docs_path, glob='**/*.txt', loader_cls=TextLoader)
    raw_documents = loader.load()

    # split documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)

    return documents


def init_chromadb(documents):
    """
    Set Up Embeddings and Chroma Vector Database
    """

    '''
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.environ.get("AZURE_DEPLOYMENT_EMBEDDINGS"),
        openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    )
    '''

    '''
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=constants.HF_MODEL_EMBEDDINGS,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    '''

    '''
    embeddings = HuggingFaceBgeEmbeddings()
    '''

    # set up embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=constants.OPENAI_API_KEY)

    # Set up chroma database
    db = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory="chroma_db",
    )

    return db


def configure_llm():
    """
    Configure the Language Model
    """

    '''
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        verbose=False,
        temperature=0.3,
    )
    '''

    '''
    llm = AutoModelForCausalLM.from_pretrained(
            constants.AUTO_MODEL_FOR_CASUAL_LLM,
            device_map='auto',
            torch_dtype=torch.float32,
            token=True,
            load_in_8bit=False
        )
    '''

    # Configure LLM
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=constants.OPENAI_API_KEY)

    return llm


def create_prompt():
    """
    Create the Prompt Template
    """

    # create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an AI Chatbot. 
                   Given only the following context: {context}
                   Answer the following question: {question}
                   AI: """,
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )

    return prompt


def create_chain(prompt, llm):
    """
    Create the LLM Chain
    """

    # create llm chain with the prompt template
    chain = prompt | llm

    ''' 
    # Create a Conversational Retrieval Chain
    
    # create pipeline + tokenizer
     
    self.chain = ConversationalRetrievalChain.from_llm(
        pipeline,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 1}),
        condense_question_prompt=prompt,
        return_source_documents=True
    )    
    '''

    return chain


def query_chromadb(db, query, chain):

    # perform similarity search in chroma database
    documents = db.similarity_search_with_score(query, 3)

    # generate response using LLM
    response = chain.invoke(
        {
            "question": query,
            "context": documents, #[0].page_content,
        }
    )

    return response


def main():
    """
    Build the Chatbot with CLI Interface
    """

    txt_docs = load_and_split_docs()
    chroma_db = init_chromadb(txt_docs)
    openai_llm = configure_llm()
    chat_prompt = create_prompt()
    conv_chain = create_chain(chat_prompt, openai_llm)

    print("\nHello! I am a chatbot. I can answer questions based on the content of a vector database of documents.\n")

    while True:
        current_datetime = datetime.now()
        user_input = input("Do you have any questions? To exit, type 'bye': ")

        if user_input.lower() == "bye":
            print("\nBye! Have a nice day!\n")
            break

        answer = query_chromadb(chroma_db, user_input, conv_chain)

        elapsed_time = datetime.now() - current_datetime

        print("\nChatbot: ", answer.content)
        print("\n Time elapsed: ", elapsed_time.total_seconds(), "seconds \n")


if __name__ == '__main__':
    main()
