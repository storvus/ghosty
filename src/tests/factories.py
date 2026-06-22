import uuid
from datetime import datetime, timezone

import factory

from src.models import Conversation, Message, User
from src.models.conversation import ConversationType
from src.utils import hash_password


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"testuser_{n}")
    password_hash = factory.LazyFunction(lambda: hash_password("Pass123!"))


class ConversationFactory(factory.Factory):
    class Meta:
        model = Conversation

    type = ConversationType.direct
    conversation_key = factory.LazyFunction(lambda: str(uuid.uuid4()))


class MessageFactory(factory.Factory):
    class Meta:
        model = Message

    client_message_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    text = factory.Sequence(lambda n: f"message {n}")
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    # sender_id and conversation_id must always be provided explicitly
