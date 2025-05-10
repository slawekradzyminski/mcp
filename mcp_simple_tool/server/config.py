"""Configuration settings for the MCP server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCP server settings."""

    port: int = 7000
    user_agent: str = "MCP Website Fetcher"

    model_config = SettingsConfigDict(env_prefix="MCP_")
