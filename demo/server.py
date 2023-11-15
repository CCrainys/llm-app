# Parse command line arguments

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--port", "-p", type=int, nargs="?", help="Port number of local LLM server"
)
parser.add_argument(
    "--local-model", "-l", type=str, nargs="?", help="Path of local model"
)
parser.add_argument("--ip", "-i", type=str, nargs="?", help="IP address of Milvus")

args = parser.parse_args()

from langchain.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")

# Split
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(loader.load())


# Store splits

from langchain.embeddings import HuggingFaceEmbeddings

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": False}
hf = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

from langchain.vectorstores import Milvus

host = args.ip if args.ip else "localhost"

# RAG prompt
from langchain import hub

rag_prompt = hub.pull("rlm/rag-prompt")

port = args.port if args.port else 8000
model_name = args.local_model if args.local_model else "tiiuae/falcon-rw-7b"

# LLM
from langchain.llms import VLLMOpenAI

llm = VLLMOpenAI(
    openai_api_key="EMPTY",
    openai_api_base=f"http://localhost:{port}/v1",
    model_name=model_name,
    model_kwargs={"stop": ["."]},
    temperature=0,
    max_tokens=20,
)

# RAG chain

from langchain.schema.runnable import RunnablePassthrough


# def get_retriever():
vectorstore = Milvus.from_documents(
    documents=all_splits,
    embedding=hf,
    connection_args={"host": host, "port": "19530"},
)
retriever = vectorstore.as_retriever()
# return retriever


# start a web server

from fastapi import FastAPI
import uvicorn
import time

app = FastAPI()

@app.get("/")
async def ask(prompt: str):
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} | rag_prompt | llm
    )
    result = rag_chain.invoke(prompt)
    answer = result[:-10]
    inference_time = result[-10:]
    return {"answer": answer, "inference_time": inference_time}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
