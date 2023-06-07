import uuid
from typing import List

from pydantic import BaseModel, Field


class MessageEnvelope(BaseModel):
    messageId: uuid.UUID
    conversationId: uuid.UUID
    messageType: List[str]
    message: BaseModel
