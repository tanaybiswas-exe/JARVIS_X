from typing import List, Dict, Any

class EphemeralMemoryBuffer:
    def __init__(self, capacity: int = 15):
        self.capacity = capacity
        self.system_prompt: Dict[str, str] = {
            "role": "system",
            "content": (
                "You are JARVIS-X: an advanced, precise, operating assistant built for high-performance computing.\n"
                "Communicate concisely, professionally, and with calculated sophistication.\n"
                "Execute tasks via available tools when action is requested.\n"
                "Never disclose private reasoning steps. Respond strictly with operational status updates."
            )
        }
        self.history: List[Dict[str, Any]] = []

    def append(self, role: str, content: str | None, tool_calls: Any = None, name: str = None) -> None:
        message: Dict[str, Any] = {"role": role}
        if content is not None:
            message["content"] = content
        if tool_calls is not None:
            message["tool_calls"] = tool_calls
        if name is not None:
            message["name"] = name
        
        self.history.append(message)
        if len(self.history) > self.capacity:
            self.history.pop(0)

    def get_payload(self) -> List[Dict[str, Any]]:
        return [self.system_prompt] + self.history

    def clear(self) -> None:
        self.history.clear()