from pydantic import BaseModel

class Comment(BaseModel):
    user_id: str = None
    cve: str = None
    content: str = None
