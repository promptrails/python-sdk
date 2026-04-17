from dataclasses import dataclass

from ._version import VERSION


@dataclass
class Config:
    api_key: str
    base_url: str = "https://api.promptrails.ai"
    timeout: float = 30.0
    max_retries: int = 3

    def __post_init__(self):
        self.base_url = self.base_url.rstrip("/")

    @property
    def headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"promptrails-python/{VERSION}",
        }
