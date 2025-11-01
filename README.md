# RAG Personal Assistant

A minimal Retrieval-Augmented Generation (RAG) chatbot with a local + OpenAI hybrid design.

* **Backend:** FastAPI (Python)
* **Frontend:** React (Vite) at `ui/`
* **Vector DB:** Chroma (local, persisted in `.chroma/`)
* **Embeddings:** Local (SentenceTransformers) **or** OpenAI (`text-embedding-3-small`)
* **LLM:** OpenAI Chat models (default `gpt-5-nano`)
* **Tokenization:** Local `tiktoken` for estimates + OpenAI usage stats

---

## Quick Start (Windows PowerShell)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env   # set OPENAI_API_KEY if you want model answers
```

### Embeddings backend

* **Local (free):**

  ```bash
  pip install sentence-transformers
  ```

  and set `EMBEDDINGS_BACKEND=local` in `.env`.
* **OpenAI (paid):** keep `EMBEDDINGS_BACKEND=openai` and set
  `OPENAI_EMBED_MODEL=text-embedding-3-small`.

---

## Ingest Knowledge

```bash
# optional reset
Remove-Item -Recurse -Force .chroma -ErrorAction Ignore
python scripts\ingest.py data\sample_kb
```

---

## Run API

```bash
uvicorn app.main:app --reload --port 8000
# http://127.0.0.1:8000/docs -> POST /chat
```

---

## Frontend (React UI)

```bash
cd ui
npm install
npm run dev
# open http://127.0.0.1:5173
```

* Toggle **Debug** to view context, diagnostics, and token estimates.
* CORS origins are configured via ALLOWED_ORIGINS in .env.

---

## RAG Flow

1. **Ingest** → chunk → embed → store in Chroma.
2. **Retrieve** → top-k similarity search (`RAG_TOP_K` in `.env`).
3. **Generate** → build prompt, send to model, return concise answer.

Token costs and context size are automatically managed:

* Input capped by `MAX_INPUT_TOKENS`
* Output capped adaptively by `MAX_OUTPUT_TOKENS`
* All token counts tracked locally (`tiktoken`) and by the OpenAI response

---

## Debug & Token Details

* Use `?debug=true` on any `/chat` request to see:

  * `context_preview`
  * model diagnostics (finish reason, length, etc.)
  * local `pre_est_input_tokens`
* You can just toggle the **Debug** checkbox in the UI for the same effect.

---

## Typical Costs

| Component         | Backend                | Cost                           |
| ----------------- | ---------------------- | ------------------------------ |
| Local embeddings  | SentenceTransformers   | $0                             |
| OpenAI embeddings | text-embedding-3-small | per token (~$0.02–$0.1 per 1M) |
| Chat completion   | e.g. `gpt-5-nano`      | ~$0.05/M input, ~$0.4/M output |

Small KBs usually cost well under a cent per request.

For that reason - feel free to experiment! See an example of my usage dashboard and cost

---

## Troubleshooting

* Empty answers → check `.md` text, then re-ingest.
* Changed embedding backend → delete `.chroma` and re-ingest.
* `"finish_reason": "length"` → increase `MAX_OUTPUT_TOKENS`.
* UI connection errors → ensure backend runs at `http://127.0.0.1:8000`.

---

## Next possible Steps (for me)

* Add ingestion for PDFs / HTML / images.
* Add snippet-based citations in answers.
* Add a simple RAG evaluation harness (golden Q/A pairs).
* Optional: experiment with local generation models (Ollama, vLLM).

---
