from pydantic import BaseModel

class Comment(BaseModel):
    user_id: str = None
    content: str = None
    report_id: str = None
