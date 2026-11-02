import asyncio
from contextlib import AsyncExitStack
from typing import Any

import httpx

from anthropic import Anthropic
from client import MCPClient
from dotenv import load_dotenv

load_dotenv()


class ChatHost:
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [MCPClient("./weather_USA.py"),MCPClient("./weather_Israel.py")]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()
        # Conversation history, kept across queries
        self.messages: list[dict[str, Any]] = []
        # self.anthropic = Anthropic()
        # For Netfree
        transport = httpx.HTTPTransport(verify=False)
        self.anthropic = Anthropic(http_client=httpx.Client(transport=transport))

    async def connect_mcp_clients(self):
        """Connect all configured MCP clients once."""
        if self.clients_connected:
            return

        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()

        if not self.mcp_clients:
            raise RuntimeError("No MCP clients are connected")

        self.clients_connected = True

    async def get_available_tools(self) -> list[dict[str, Any]]:
        """Collect tools from all MCP clients and map them back to their owner."""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        available_tools: list[dict[str, Any]] = []

        for client in self.mcp_clients:
            if client.session is None:
                print(f"Warning: MCP client {client.client_name} is not connected, skipping")
                continue

            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    if exposed_name in self.tool_clients:
                        raise RuntimeError(f"Duplicate tool name detected: {exposed_name}")

                    self.tool_clients[exposed_name] = (client, tool.name)
                    available_tools.append(
                        {
                            "name": exposed_name,
                            "description": f"[{client.client_name}] {tool.description}",
                            "input_schema": tool.inputSchema,
                        }
                    )
            except Exception as e:
                print(f"Warning: Failed to get tools from {client.client_name}: {str(e)}")
                continue

        if not available_tools:
            raise RuntimeError("No tools available from any MCP client")

        return available_tools


    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        history_length = len(self.messages)
        try:
            return await self._run_query(query)
        except Exception:
            # Drop the partial turn so the history stays valid for the next query
            del self.messages[history_length:]
            raise

    async def _run_query(self, query: str) -> str:
        messages = self.messages
        messages.append({"role": "user", "content": query})
        available_tools = await self.get_available_tools()
        final_text = []

        while True:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                messages=messages,
                tools=available_tools
            )

            assistant_message_content = []
            tool_results = []
            saw_tool_use = False

            for content in response.content:
                assistant_message_content.append(content)

                if content.type == 'text':
                    final_text.append(content.text)
                    continue

                if content.type != 'tool_use':
                    continue

                saw_tool_use = True
                tool_name = content.name
                tool_args = content.input

                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Tool failures are reported back to Claude instead of aborting the query
                try:
                    if tool_name not in self.tool_clients:
                        raise RuntimeError(f"Unknown tool requested by model: {tool_name}")

                    client, original_tool_name = self.tool_clients[tool_name]
                    if client.session is None:
                        raise RuntimeError(f"MCP client {client.client_name} is not connected")

                    result = await client.session.call_tool(original_tool_name, tool_args)
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result.content,
                        "is_error": bool(result.isError),
                    }
                except Exception as e:
                    final_text.append(f"[Tool {tool_name} failed: {e}]")
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": f"Tool call failed: {e}",
                        "is_error": True,
                    }

                tool_results.append(tool_result)

            messages.append({
                "role": "assistant",
                "content": assistant_message_content
            })

            if not saw_tool_use:
                break

            messages.append({
                "role": "user",
                "content": tool_results
            })

        return "\n".join(final_text)
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                
                response = await self.process_query(query)
                print("\n" + response)
                
            except Exception as e:
                print(f"\nchat_loop Error: {str(e)}")
                
    async def cleanup(self):
        """Clean up resources"""
        for client in reversed(self.mcp_clients):
            await client.cleanup()
        await self.exit_stack.aclose()
        
        
async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        await host.cleanup()
        
if __name__ == "__main__":
    asyncio.run(main())
