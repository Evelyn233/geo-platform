import os
import sys
import asyncio
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.utils import EmbeddingFunc


app = FastAPI(title="RAG-Anything Backend", version="0.1.0")


# Global RAG instance
rag_instance: Optional[RAGAnything] = None
initialized: bool = False


def _get_model_name() -> str:
    return os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")


def doubao_complete(prompt=None, system_prompt=None, history_messages=None, messages=None, model=None, temperature=0.1, max_tokens=4000, **kwargs):
    import time
    import requests

    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set in environment")

    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    model = model or _get_model_name()

    if messages is not None:
        msg_list = messages
    else:
        msg_list = []
        if system_prompt:
            msg_list.append({"role": "system", "content": system_prompt})
        if history_messages:
            msg_list.extend(history_messages)
        if prompt:
            msg_list.append({"role": "user", "content": prompt})

    data = {"model": model, "messages": msg_list, "temperature": temperature, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    backoffs = [0, 5, 15, 30]
    last_err = None
    for delay in backoffs:
        if delay:
            time.sleep(delay)
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=120)
            resp.raise_for_status()
            j = resp.json()
            return j["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if "429" in str(e):
                continue
            break
    raise last_err if last_err else RuntimeError("Doubao request failed")


def doubao_embed(texts: List[str]) -> List[List[float]]:
    import time
    import requests

    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set in environment")

    url = "https://ark.cn-beijing.volces.com/api/v3/embeddings"
    model = os.getenv("DOUBAO_EMBED_MODEL", "ep-20240613094406-3v7ht")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    backoffs = [0, 5, 15]
    last_err = None
    for delay in backoffs:
        if delay:
            time.sleep(delay)
        try:
            resp = requests.post(url, json={"model": model, "input": texts}, headers=headers, timeout=120)
            resp.raise_for_status()
            j = resp.json()
            return [d["embedding"] for d in j.get("data", [])]
        except Exception as e:
            last_err = e
            if "429" in str(e):
                continue
            break
    raise last_err if last_err else RuntimeError("Doubao embedding failed")


async def async_doubao_embed(texts: List[str]) -> List[List[float]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: doubao_embed(texts))


async def ensure_initialized(working_dir: str = "./rag_storage") -> bool:
    global rag_instance, initialized
    if initialized and rag_instance is not None:
        return True

    # Prepare config
    config = RAGAnythingConfig(working_dir=working_dir)

    embedding_func = EmbeddingFunc(embedding_dim=2048, max_token_size=8192, func=async_doubao_embed)

    rag_instance = RAGAnything(
        config=config,
        llm_model_func=doubao_complete,
        embedding_func=embedding_func,
        lightrag_kwargs={"tiktoken_model_name": "gpt-3.5-turbo"},
    )

    # Make sure LightRAG is ready
    await rag_instance._ensure_lightrag_initialized()
    initialized = True
    return True


@app.post("/init")
async def api_init(working_dir: str = Form(default="./rag_storage")):
    ok = await ensure_initialized(working_dir)
    return {"initialized": ok, "working_dir": working_dir, "model": _get_model_name()}


@app.post("/ingest/upload")
async def ingest_upload(file: UploadFile = File(...), parse_method: str = Form(default=None)):
    await ensure_initialized()

    tmp_dir = Path("./uploads")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / file.filename
    content = await file.read()
    tmp_path.write_bytes(content)

    # Use high-level pipeline: document parsing + insertion
    await rag_instance.process_documents_with_rag_batch([str(tmp_path)], parse_method=parse_method)
    return {"status": "ok", "file": file.filename}


@app.post("/ingest/paths")
async def ingest_paths(paths: List[str]):
    await ensure_initialized()
    await rag_instance.process_documents_with_rag_batch(paths)
    return {"status": "ok", "count": len(paths)}


@app.post("/query")
async def api_query(q: str, mode: str = "mix"):
    await ensure_initialized()
    try:
        result = await rag_instance.aquery(q, mode=mode)
        return {"answer": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/stats")
async def api_stats():
    await ensure_initialized()
    l = rag_instance.lightrag
    # basic stats from storages
    text_chunks = await l.text_chunks.count()
    entities = await l.entities_vdb.count()
    rels = await l.relationships_vdb.count()
    return {"text_chunks": text_chunks, "entities": entities, "relationships": rels}


@app.get("/")
async def root():
    return {"service": "RAG-Anything", "status": "ok"}


