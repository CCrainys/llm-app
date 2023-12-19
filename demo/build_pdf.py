import os
from tqdm import tqdm
from langchain.vectorstores import Milvus
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings

model_name = "sentence-transformers/all-mpnet-base-v2"  # embedding 大小是 768
model_kwargs = {"device": "cuda"}
encode_kwargs = {"normalize_embeddings": False}
hf = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

total_files = 0
all_splits: list[Document] = []

for dir in os.listdir("/home/v-kunzhaoxu/arXiv_dataset/cs/"):
    total_files += len(os.listdir(os.path.join("/home/v-kunzhaoxu/arXiv_dataset/cs/", dir)))

with tqdm(total=total_files) as pbar:
    for dir in os.listdir("/home/v-kunzhaoxu/arXiv_dataset/cs/"):
        for file in os.listdir(os.path.join("/home/v-kunzhaoxu/arXiv_dataset/cs/", dir)):
            try:
                loader = PyPDFLoader(
                    os.path.join("/home/v-kunzhaoxu/arXiv_dataset/cs/", dir, file)
                )
                all_splits += text_splitter.split_documents(loader.load())
                pbar.update(1)
            except Exception as e:
                print(os.path.join(dir, file), "error")
                print(e)
                # os.remove(os.path.join("/home/v-kunzhaoxu/arXiv_dataset/cs/", dir, file))
                pbar.update(1)

vectorstore = Milvus.from_documents(
    documents=all_splits,
    embedding=hf,
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="TestLangchain",
    index_params={
        "metric_type": "L2",
        "index_type": "GPU_IVF_PQ",
        "params": {"nlist": 128, "m": 4, "nbits": 8},
    },
)
