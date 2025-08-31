from datetime import datetime
from typing import Iterable

import httpx

class FonteClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def fetch_data(self, start: datetime, end: datetime, variables: Iterable[str] | None = None) -> list[dict]:
        params = {"start": start.isoformat(), "end": end.isoformat()}
        if variables:
            for v in variables:
                params.setdefault("variables", []).append(v)

        with httpx.Client(base_url=self.base_url, timeout=30) as client:
            resp = client.get("/data", params=params)
            resp.raise_for_status()
            return resp.json()