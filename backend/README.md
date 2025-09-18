RAG-Anything Backend (FastAPI)

Quick start

1. Set environment variables:

   - `ARK_API_KEY`: DouBao API key
   - optional `DOUBAO_MODEL` and `DOUBAO_EMBED_MODEL`

2. Install deps (recommended inside a venv):

```
pip install -r requirements.txt
```

3. Run server:

```
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

API

- POST `/init` (form: `working_dir`): initialize RAG storages
- POST `/ingest/upload` (multipart file, optional `parse_method`): parse and insert
- POST `/ingest/paths` (json array of paths): batch parse/insert for files or folders
- POST `/query` (query params `q`, optional `mode`): ask
- GET `/stats`: storage counts


