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
)

# RAG chain

from langchain.schema.runnable import RunnablePassthrough


def get_retriever():
    vectorstore = Milvus.from_documents(
        documents=all_splits,
        embedding=hf,
        connection_args={"host": host, "port": "19530"},
    )
    retriever = vectorstore.as_retriever()
    return retriever


# start a web server

from sanic import Sanic
from sanic.response import text

app = Sanic("app")

import time

@app.get("/")
async def ask(request):
    prompt = request.args.get("prompt", "What is Task Decomposition?")
    time1 = time.time()
    retriever = await request.app.loop.run_in_executor(None, get_retriever)
    time2 = time.time()
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} | rag_prompt | llm
    )
    time3 = time.time()
    result = await request.app.loop.run_in_executor(None, rag_chain.invoke, prompt)
    time4 = time.time()
    print("Retriever time:", time2 - time1)
    print("Creation time:", time3 - time2)
    print("Invoke time:", time4 - time3)
    return text(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
