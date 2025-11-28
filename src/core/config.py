import os
from typing import Optional


class Config:
    def __init__(self):
        self.kaspa_rpc_url: str = os.getenv("KASPA_RPC_URL", "http://localhost:16110")
        self.kasfyi_api_key: Optional[str] = os.getenv("KASFYI_API_KEY")
        self.kasfyi_base_url: str = os.getenv("KASFYI_BASE_URL", "https://api.kas.fyi")
        self.kasfyi_rate_limit: float = float(os.getenv("KASFYI_RATE_LIMIT", "1.0"))
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"


config = Config()