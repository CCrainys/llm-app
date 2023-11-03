# Parse command line arguments
import argparse
parser = argparse.ArgumentParser()  
  
# 添加参数  
parser.add_argument('--port', '-p', type=int, nargs='?', help='Port number of local LLM server')

parser.add_argument('--local-model', '-l', type=str, nargs='?',
                    help='Path of local model')

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
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

from langchain.vectorstores import Chroma
vectorstore = Chroma.from_documents(documents=all_splits, embedding=hf)
retriever = vectorstore.as_retriever()

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
    model_kwargs={"stop": ["."]}
)

# RAG chain

from langchain.schema.runnable import RunnablePassthrough

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | rag_prompt | llm

res = rag_chain.invoke("What is Task Decomposition?")

print(res)
