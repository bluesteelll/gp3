import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parents[1]
SESSIONS_DIR = ROOT / "data" / "sessions"
SUBFOLDERS = ["raw", "processed", "reports", "models"]


def create_session():
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = SESSIONS_DIR / session_id
    for sub in SUBFOLDERS:
        (session_dir / sub).mkdir(parents=True, exist_ok=True)

    update_meta(
        session_dir,
        session_id=session_id,
        started_at=datetime.now().isoformat(),
        status="running",
    )
    return session_id, session_dir


def update_meta(session_dir, **fields):
    meta_path = session_dir / "session.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta.update(fields)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def save_artifact(session_dir, subfolder, filename, content):
    path = session_dir / subfolder / filename
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(str(content), encoding="utf-8")
    return path
