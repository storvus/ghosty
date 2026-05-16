from unittest.mock import Mock, AsyncMock

import pytest

from src.constants import Presence, ConnectionState
from src.tests.mocks.session import MockedClientSession


@pytest.fixture
def app_state():
    app_state = Mock()
    app_state.get_presence.return_value = Presence.ONLINE
    app_state.get_user_connections.return_value = [MockedClientSession(user_id="user1", state=ConnectionState.ACTIVE)]
    app_state.get_friend_user_ids = AsyncMock(side_effect=lambda user_id: ["friend1", "friend2"])
    app_state.get_invisible_exception_user_ids = AsyncMock(side_effect=lambda user_id: ["friend2"])
    yield app_state
