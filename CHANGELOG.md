## Release v0.1.0 - Initial Stable Local RAG Core

### Overview

This release establishes a stable, developer-friendly foundation for the RAG Personal Assistant project, integrating a secure FastAPI backend, local and OpenAI embeddings, and a working React chat UI.

### Backend and API

* Refactored configuration with clean `.env` management.

  * Added `DEBUG` and `ALLOWED_ORIGINS`.
  * Removed unused cost caps.
* Safer, configurable CORS via `.env` (no wildcards, no credentials).
* Added `/chat` endpoint with `?debug=true` support for context and diagnostics.
* Added `/models/list` endpoint via `ModelManager`.

### RAG Pipeline

* Integrated `ModelManager` for cost estimation and token caps.
* Added `TokenAnalyzer` (via `tiktoken`) for local token counting.
* Included pre-call token estimation in debug responses.
* Added detailed model diagnostics (`finish_reason`, `content_len`, etc.).

### Frontend (React UI)

* Added Debug toggle to show token counts, context, and diagnostics.
* Connected API base via `VITE_API_BASE` for configurable deployment.
* Improved token and source display in chat responses.

### Documentation

* Added `.env.example` for quick local setup.
* Updated README with:

  * Full setup steps (Windows/PowerShell).
  * Explanation of `.env` variables.
  * Updated CORS and debug notes.

### Technical Stack

* FastAPI backend.
* Chroma vector database (local persistent store).
* tiktoken for token estimation.
* OpenAI (default `gpt-5-nano`) or local SentenceTransformers embeddings.
* React (Vite) frontend.

### Highlights

* Reliable local setup with configurable backends.
* Transparent token tracking and debugging.
* Secure, minimal API design ready for expansion to PDF and image ingestion.
