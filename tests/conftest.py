"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from blueplane.config import Config
from blueplane.storage.sqlite_traces import SQLiteTraceStorage
from blueplane.storage.sqlite_conversations import ConversationStorage
from blueplane.storage.redis_metrics import RedisMetricsStorage


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config(temp_data_dir):
    """Create a test configuration."""
    config = Config(
        data_dir=temp_data_dir,
        db_path=temp_data_dir / "test_telemetry.db",
        redis_host="localhost",
        redis_port=6379,
    )
    return config


@pytest.fixture
def sqlite_trace_storage(test_config):
    """Create a SQLite trace storage for testing."""
    storage = SQLiteTraceStorage(db_path=test_config.db_path)
    yield storage
    storage.close()


@pytest.fixture
def conversation_storage(test_config):
    """Create a conversation storage for testing."""
    storage = ConversationStorage(db_path=test_config.db_path)
    yield storage
    storage.close()


@pytest.fixture
def redis_metrics_storage():
    """Create a Redis metrics storage for testing."""
    storage = RedisMetricsStorage()
    yield storage
    storage.close()

