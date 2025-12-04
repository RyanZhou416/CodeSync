import hashlib
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
import uvicorn
from typing import Dict, List

app = FastAPI()

project_store: Dict[str, str] = {}
hash_cache: Dict[str, str] = {}
config_store: Dict[str, List[str]] = {}


def calculate_hash(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()


@app.get("/", response_class=HTMLResponse)
async def index():
    links = "".join([f'<li><a href="/{k}">{k}</a></li>' for k in project_store.keys()])
    return f"<h1>Code Context Server</h1><ul>{links}</ul>"


@app.post("/upload/{project_name}")
async def upload_project(project_name: str, request: Request):
    content = await request.body()
    text_data = content.decode("utf-8", errors="replace")
    project_store[project_name] = text_data
    hash_cache[project_name] = calculate_hash(text_data)
    return {"status": "success", "hash": hash_cache[project_name]}


@app.get("/{project_name}", response_class=PlainTextResponse)
async def get_project(project_name: str):
    if project_name not in project_store:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_store[project_name]


@app.get("/hash/{project_name}")
async def get_project_hash(project_name: str):
    if project_name not in hash_cache: return {"hash": None}
    return {"hash": hash_cache[project_name]}


@app.post("/config/{project_name}")
async def save_config(project_name: str, request: Request):
    try:
        config_store[project_name] = await request.json()
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/config/{project_name}")
async def get_config(project_name: str):
    return config_store.get(project_name, [])


# === 新增：删除接口 ===
@app.delete("/project/{project_name}")
async def delete_project(project_name: str):
    deleted = False
    if project_name in project_store:
        del project_store[project_name]
        deleted = True
    if project_name in hash_cache:
        del hash_cache[project_name]
    if project_name in config_store:
        del config_store[project_name]

    return {"status": "deleted" if deleted else "not_found"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)