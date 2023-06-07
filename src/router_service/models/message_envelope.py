"""
MessageEnvelope model.
"""
import uuid
from typing import List

from pydantic import BaseModel


class MessageEnvelope(BaseModel):
    """
    The pydantic MessageEnvelope model for use in masstransit messaging.
    """

    messageId: uuid.UUID
    conversationId: uuid.UUID
    messageType: List[str]
    message: BaseModel
