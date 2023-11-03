# README

## Dependencies

```bash
pip install langchain bs4 sentence-transformers chromadb langchainhub openai pymilvus
```

## Usage

1. Start a server on local port 8000

```bash
python -m vllm.entrypoints.openai.api_server --model tiiuae/falcon-rw-7b --tensor-parallel-size 1
```

You can increase the value of `tensor-parallel-size` to at most the number of GPUs on your device.

2. Send message to LLM

```bash
python chatpdf.py
```
