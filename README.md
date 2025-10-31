# RAG Personal Assistant

A minimal Retrieval‑Augmented Generation (RAG) chatbot.

* **Backend:** FastAPI
* **Vector DB:** Chroma (local, persisted in `.chroma/`)
* **Embeddings:** **Local** (SentenceTransformers) or **OpenAI** (`text-embedding-3-small`)
* **LLM:** OpenAI Chat (e.g., `gpt-4o-mini`)

## Quick Start (Windows PowerShell)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env   # set OPENAI_API_KEY if you want model answers
```

### Choose embeddings backend

* **Local (free):** set `EMBEDDINGS_BACKEND=local` in `.env`, then:

  ```bash
  pip install sentence-transformers
  ```
* **OpenAI (paid, cheap):** keep `EMBEDDINGS_BACKEND=openai` and set `OPENAI_API_KEY`, `OPENAI_EMBED_MODEL=text-embedding-3-small`.

### Ingest knowledge

```bash
# optional reset
Remove-Item -Recurse -Force .chroma -ErrorAction Ignore
python scripts\ingest.py data\sample_kb
```

### Run API

```bash
uvicorn app.main:app --reload --port 8000
# http://127.0.0.1:8000/docs -> POST /chat
```

## Token Tools (optional)

* CLI:

  ```bash
  python scripts\tokens.py --text "Explain Canonicar briefly."
  python scripts\tokens.py --file data\sample_kb\01_canonicar_overview.md
  ```
* API:

  * `POST /tools/tokens/text`
  * `POST /tools/tokens/messages`

## RAG Flow

1. **Ingest** → chunk → embed → store in Chroma (`kb_main`).
2. **Retrieve** → top‑k similarity search.
3. **Generate** → LLM answers using retrieved context.

## Costs (where you pay)

* **Local embeddings:** $0
* **OpenAI embeddings:** per‑token (very small for small KBs)
* **/chat generation:** per‑token (input + output).
  Small tests are typically **fractions of a cent**. OpenAI usage rounds to cents, so you may see $0.00 even when tokens increase.

## Troubleshooting

* Use `http://127.0.0.1:8000` (port 8000).
* Empty answers → ensure `.md` files have text and re‑ingest.
* Switched embeddings backend → delete `.chroma` and re‑ingest.
* CORS for UI → enable `CORSMiddleware` in `app/main.py` when adding a front‑end.

## What’s Next

* Add PDF/HTML ingestion adapters.
* Add React chat UI (`ui/` with Vite) and CORS.
* Add citations with short snippets in answers.
* Add a tiny evaluation harness for RAG (golden Q/A file).
* Optional: try an OSS generation model later (Ollama/vLLM).
