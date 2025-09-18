import os
import asyncio
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

# Add project root to path
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

app = FastAPI(title="RAG-Anything Simple Backend", version="0.1.0")

# Global state
rag_initialized = False
working_dir = "./rag_storage"

def doubao_complete(prompt=None, system_prompt=None, history_messages=None, messages=None, model=None, temperature=0.1, max_tokens=4000, **kwargs):
    import time
    import requests

    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("ARK_API_KEY is not set in environment")

    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    model = model or os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")

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

@app.post("/init")
async def api_init(working_dir_param: str = Form(default="./rag_storage")):
    global rag_initialized, working_dir
    working_dir = working_dir_param
    
    # Check if rag_storage exists
    if not os.path.exists(working_dir):
        return {"error": f"Working directory {working_dir} does not exist"}
    
    rag_initialized = True
    return {"initialized": True, "working_dir": working_dir, "model": os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")}

@app.post("/query")
async def api_query(q: str, mode: str = "mix"):
    if not rag_initialized:
        return JSONResponse(status_code=400, content={"error": "RAG not initialized. Call /init first."})
    
    try:
        # Use simple query approach from existing examples
        from simple_query import ask_question, load_document_content
        
        # Load document content from rag_storage
        document_content = load_document_content()
        if not document_content:
            return {"error": "No document content found in rag_storage"}
        
        # Ask question using existing simple query logic
        result = ask_question(q, document_content)
        return {"answer": result}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/stats")
async def api_stats():
    if not rag_initialized:
        return JSONResponse(status_code=400, content={"error": "RAG not initialized. Call /init first."})
    
    try:
        # Simple stats from rag_storage directory
        if not os.path.exists(working_dir):
            return {"error": "Working directory not found"}
        
        files = list(Path(working_dir).glob("*.json"))
        return {
            "working_dir": working_dir,
            "storage_files": len(files),
            "status": "ready"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    return {"service": "RAG-Anything Simple Backend", "status": "ok", "initialized": rag_initialized}
