import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException
from apps.api.app.schemas.tool import ToolDefinition

router = APIRouter(prefix="/tools", tags=["Tools"])

def _load_tools_json() -> List[dict]:
    possible_paths = [
        Path("/app/packages/tool-registry/tools.json"),
        Path("/app/apps/web/src/data/tools.json"),
        Path(__file__).resolve().parent.parent.parent.parent.parent / "packages" / "tool-registry" / "tools.json",
        Path(__file__).resolve().parent.parent.parent.parent / "web" / "src" / "data" / "tools.json",
        Path("./packages/tool-registry/tools.json"),
        Path("./apps/web/src/data/tools.json"),
    ]
    for p in possible_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return []

@router.get("", response_model=List[ToolDefinition])
async def list_tools():
    """Retrieve all available tools from the central Tool Registry."""
    return _load_tools_json()

@router.get("/{slug}", response_model=ToolDefinition)
async def get_tool(slug: str):
    """Retrieve metadata and schema for a specific tool by its URL slug."""
    tools = _load_tools_json()
    for t in tools:
        if t.get("slug") == slug:
            return t
    raise HTTPException(status_code=404, detail=f"Tool with slug '{slug}' not found.")
