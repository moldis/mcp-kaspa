import os
from typing import Optional


class Config:
    def __init__(self):
        self.kaspa_rpc_url: str = os.getenv("KASPA_RPC_URL", "http://localhost:16110")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"


config = Config()