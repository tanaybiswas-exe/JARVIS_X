import json
from typing import Dict, Any, Callable, Awaitable
from backend.ai.provider import BaseAIProvider
from backend.memory.buffer import EphemeralMemoryBuffer
from backend.tools.registry import tool_registry

class AIOrchestrator:
    def __init__(self, provider: BaseAIProvider):
        self.provider = provider
        self.memory = EphemeralMemoryBuffer()

    async def process_user_turn(
        self, 
        user_text: str, 
        event_callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> str:
        self.memory.append(role="user", content=user_text)
        tools = tool_registry.get_all_schemas()

        await event_callback({"type": "status", "detail": "Reasoning over incoming vectors..."})
        response = await self.provider.chat_completion(self.memory.get_payload(), tools=tools)

        if "tool_calls" in response and response["tool_calls"]:
            self.memory.append(
                role="assistant", 
                content=response.get("content"), 
                tool_calls=response["tool_calls"]
            )
            for tool_call in response["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                raw_args = tool_call["function"]["arguments"]
                call_id = tool_call["id"]

                await event_callback({
                    "type": "tool_executing",
                    "tool": tool_name,
                    "payload": raw_args
                })

                tool_inst = tool_registry.get_tool(tool_name)
                if not tool_inst:
                    tool_result = {"status": "Error", "message": f"Tool '{tool_name}' missing from system registry."}
                else:
                    try:
                        kwargs = json.loads(raw_args)
                        tool_result = await tool_inst.run(**kwargs)
                    except Exception as e:
                        tool_result = {"status": "Error", "message": str(e)}

                await event_callback({
                    "type": "tool_finished",
                    "tool": tool_name,
                    "result": tool_result
                })

                self.memory.append(
                    role="tool",
                    content=json.dumps(tool_result),
                    name=tool_name
                )
                self.memory.history[-1]["tool_call_id"] = call_id

            await event_callback({"type": "status", "detail": "Synthesizing operation verification..."})
            final_turn = await self.provider.chat_completion(self.memory.get_payload(), tools=None)
            final_content = final_turn.get("content", "Operation completed.")
            self.memory.append(role="assistant", content=final_content)
            return final_content

        final_content = response.get("content", "Ready for commands.")
        self.memory.append(role="assistant", content=final_content)
        return final_content