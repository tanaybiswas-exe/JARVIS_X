from abc import ABC, abstractmethod
from typing import Any, Dict, List
import httpx

class BaseAIProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass

class OpenAICompatibleProvider(BaseAIProvider):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            if response.status_code != 200:
                raise RuntimeError(f"Upstream AI Provider Error: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]