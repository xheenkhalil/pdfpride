from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    id: str
    number: Optional[int] = None
    slug: str
    name: str
    category: str
    category_id: Optional[int] = None
    description: str
    icon: str
    badge: Optional[str] = None
    accepted_mimes: List[str]
    accepted_extensions: List[str]
    min_files: int = 1
    max_files: int = 20
    operation: str
    is_featured: bool = False
    options_schema: Dict[str, Any]
