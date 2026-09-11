
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import CASES_DIR, LOGS_DIR, TOOLS_DIR, get_database_path


class AppSettings(BaseSettings):
    """Core application settings populated from environment variables."""
    
    app_name: str = "TRON-DeCypher"
    app_version: str = "1.0.0"
    flag_pattern: str = "CTK{...}"
    
    env: str = Field(default="development", alias="TRON_DECYPHER_ENV")
    log_level: str = Field(default="INFO", alias="TRON_DECYPHER_LOG_LEVEL")
    
    database_url: str = Field(
        default=f"sqlite:///{get_database_path()}", 
        alias="TRON_DECYPHER_DATABASE_URL"
    )
    
    cases_path: str = Field(default=str(CASES_DIR), alias="TRON_DECYPHER_CASES_PATH")
    exports_path: str = Field(default=str(CASES_DIR), alias="TRON_DECYPHER_EXPORTS_PATH")
    temp_path: str = Field(default=str(CASES_DIR), alias="TRON_DECYPHER_TEMP_PATH")
    external_tools_path: str = ""
    yara_rules_path: str = ""
    
    # Analysis Limits
    max_artifact_size: int = Field(default=100 * 1024 * 1024, alias="TRON_DECYPHER_MAX_ARTIFACT_SIZE")
    max_output_size: int = 10 * 1024 * 1024
    max_pcap_packets: int = 100000
    max_memory_time: int = 300
    max_yara_time: int = 60
    max_disassembly_size: int = 5 * 1024 * 1024
    max_archive_size: int = 500 * 1024 * 1024
    max_decoder_recursion: int = 5
    max_decoder_pipeline_steps: int = 20
    
    # Network Safety
    offline_mode: bool = True
    authorized_hosts: str = ""
    http_timeout: int = 30
    max_response_size: int = 10 * 1024 * 1024
    max_redirects: int = 5
    require_external_auth: bool = True
    logs_path: str = Field(default=str(LOGS_DIR), alias="TRON_DECYPHER_LOGS_PATH")
    tools_path: str = Field(default=str(TOOLS_DIR), alias="TRON_DECYPHER_TOOLS_PATH")
    
    # API Keys
    anthropic_api_key: str | None = None
    anthropic_base_url: str | None = None
    anthropic_model: str | None = "claude-3-opus-20240229"
    anthropic_api_mode: str = "Mock"
    anthropic_temperature: float = 0.2
    anthropic_max_tokens: int = 4096
    anthropic_timeout: int = 30
    virustotal_api_key: str | None = None
    urlscan_api_key: str | None = None
    otx_api_key: str | None = None
    abuseipdb_api_key: str | None = None
    shodan_api_key: str | None = None
    censys_api_id: str | None = None
    censys_api_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Global settings instance
settings = AppSettings()




