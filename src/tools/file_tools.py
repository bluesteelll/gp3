from pathlib import Path

from langchain_core.tools import tool


@tool
def read_file(path):
    return Path(path).read_text(encoding="utf-8")


@tool
def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return str(p.resolve())


@tool
def list_files(path):
    return [p.name for p in Path(path).iterdir()]
