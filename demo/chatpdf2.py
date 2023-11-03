from langchain.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")

# Split
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(loader.load())


# Store splits

from langchain.embeddings import HuggingFaceEmbeddings
# model_name = "sentence-transformers/all-mpnet-base-v2"
model_name = "../../LLM/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

from langchain.vectorstores import Milvus
# vectorstore = FAISS.from_documents(documents=all_splits, embedding=hf)

#host改成服务器ip
vectorstore = Milvus.from_documents(
    documents=all_splits,
    embedding=hf,
    connection_args={"host": "192.168.1.52", "port": "19530"},
)
retriever = vectorstore.as_retriever()

# RAG prompt
from langchain import hub
rag_prompt = hub.pull("rlm/rag-prompt")

# LLM
from langchain.llms import VLLMOpenAI
llm = VLLMOpenAI(
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8000/v1",
    model_name="../../LLM/llm",
    model_kwargs={"stop": ["."]}
)

# RAG chain

from langchain.schema.runnable import RunnablePassthrough

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | rag_prompt | llm

res = rag_chain.invoke("What is Task Decomposition?")

print(res)