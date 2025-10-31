# CLI wrapper for ingestion
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ingest import ingest_dir

if __name__ == "__main__":
    dir_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_kb"
    ingest_dir(dir_path)
