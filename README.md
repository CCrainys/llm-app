# README

## Dependencies

```bash
pip install langchain bs4 sentence-transformers chromadb langchainhub openai==0.28.1 pymilvus sanic
```

## Usage

### chatpdf.py

1. Start a server on local port 8000

```bash
python -m vllm.entrypoints.openai.api_server --model tiiuae/falcon-rw-7b --tensor-parallel-size 1
```

You can increase the value of `tensor-parallel-size` to at most the number of GPUs on your device.

2. Send message to LLM

```bash
python chatpdf.py [-p port-number] [-l path-of-local-model]
```

### chatpdf2.py


1. Start a server on local port 8000

    Same as chatpdf1.py

2. Deploy Milvus database

```bash
wget https://github.com/milvus-io/milvus/releases/download/v2.3.2/milvus-standalone-docker-compose-gpu.yml -O docker-compose.yml
docker compose up -d
```

3. Send message to LLM

```bash
python chatpdf.py [-p port-number] [-l path-of-local-model] [-i ip-address-of-milvus]
```
