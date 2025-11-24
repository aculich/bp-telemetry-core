# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Configuration management for capture layer.
Loads and validates configuration from YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class RedisConfig:
    """Redis connection configuration."""
    host: str = "localhost"
    port: int = 6379
    socket_timeout: float = 1.0
    socket_connect_timeout: float = 1.0
    max_connections: int = 10


@dataclass
class StreamConfig:
    """Redis Stream configuration."""
    name: str
    max_length: int = 10000
    block_ms: int = 1000
    count: int = 100


class Config:
    """
    Configuration manager for Blueplane Telemetry Core.

    Loads configuration from YAML files in config/ directory.
    Provides convenient access to all settings.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_dir: Path to configuration directory.
                       Defaults to checking multiple locations
        """
        if config_dir is None:
            # Try multiple locations for config directory
            possible_locations = [
                # 1. User's home directory (where installer puts it)
                Path.home() / ".blueplane",
                # 2. Relative to current file (development/source)
                Path(__file__).parent.parent.parent.parent / "config",
                # 3. System-wide config
                Path("/etc/blueplane"),
            ]

            # Also walk up from current file looking for config/
            current = Path(__file__).parent
            while current != current.parent:
                config_candidate = current / "config"
                if config_candidate.exists():
                    possible_locations.insert(0, config_candidate)
                    break
                current = current.parent

            # Find first existing location
            for location in possible_locations:
                if location.exists() and location.is_dir():
                    # Check if it has any YAML files
                    if list(location.glob("*.yaml")) or list(location.glob("*.yml")):
                        config_dir = location
                        break

            if config_dir is None:
                # Use default location even if it doesn't exist
                # (will use default values)
                config_dir = Path.home() / ".blueplane"

        self.config_dir = Path(config_dir)
        self._config: Optional[Dict[str, Any]] = None

        # Load configuration
        self._load_config()

    def _load_config(self) -> None:
        """
        Load unified configuration file.

        Loads config.yaml containing
        all settings as defined in config.schema.yaml.
        """
        # Try config.yaml first (standard), then redis.yaml (existing deployments)
        config_file = self.config_dir / "config.yaml"
        if not config_file.exists():
            config_file = self.config_dir / "redis.yaml"

        if config_file.exists():
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = {}

    @property
    def redis(self) -> RedisConfig:
        """Get Redis configuration."""
        redis_data = self._config.get("redis", {})
        connection_data = redis_data.get("connection", {})
        pool_data = redis_data.get("connection_pool", {})

        return RedisConfig(
            host=connection_data.get("host", "localhost"),
            port=connection_data.get("port", 6379),
            socket_timeout=pool_data.get("socket_timeout", 5.0),
            socket_connect_timeout=pool_data.get("socket_connect_timeout", 2.0),
            max_connections=pool_data.get("max_connections", 10),
        )

    def get_stream_config(self, stream_type: str) -> StreamConfig:
        """
        Get stream configuration.

        Args:
            stream_type: Type of stream (message_queue, dlq, cdc)

        Returns:
            StreamConfig for the requested stream
        """
        streams = self._config.get("streams", {})
        stream_data = streams.get(stream_type, {})

        return StreamConfig(
            name=f"telemetry:{stream_type}",
            max_length=stream_data.get("max_length", 10000),
            block_ms=stream_data.get("block_ms", 1000),
            count=stream_data.get("count", 100),
        )

    def get_monitoring_config(self, section: str) -> Dict[str, Any]:
        """
        Get monitoring configuration for a specific section.

        Args:
            section: Monitoring section name (e.g., 'cursor_database', 'cursor_markdown')

        Returns:
            Dictionary of configuration values (empty dict if section not found)
        """
        monitoring = self._config.get("monitoring", {})
        return monitoring.get(section, {})

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get arbitrary configuration value using dot-separated path.

        The schema defines a unified config structure with sections:
        paths, redis, streams, timeouts, monitoring, batching, logging, and features.

        Args:
            key: Dot-separated key path (e.g., "redis.connection.host")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        parts = key.split(".")
        config = self._config

        # Navigate the config dict
        for part in parts:
            if isinstance(config, dict):
                config = config.get(part)
                if config is None:
                    return default
            else:
                return default

        return config if config is not None else default
