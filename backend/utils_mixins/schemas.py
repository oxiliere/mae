from typing import Optional
from ninja import Schema




class MessageSchema(Schema):
    code: Optional[int] = None
    detail: str

