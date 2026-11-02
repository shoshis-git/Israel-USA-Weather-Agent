import asyncio
import atexit
import concurrent.futures
import threading
from typing import Any, Awaitable, Callable

import gradio as gr

from host import ChatHost

PLACEHOLDER = """
### 🌦️ שלום! אפשר לשאול אותי על מזג האוויר

- מה מזג האוויר בתל אביב כרגע?
- מה מצב הרוחות והטמפרטורה בירושלים?
- יש התראות מזג אוויר בקליפורניה?
"""

CSS = """
.prose, textarea { direction: rtl; text-align: right; }
"""


class HostRunner:
    """Runs ChatHost in a single long-lived task on a background event loop.

    MCP stdio sessions must be opened and closed in the same asyncio task,
    while Gradio runs every request in a different one. So all work on the
    host is queued to one worker task that owns it for its whole lifetime.
    """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self.jobs: asyncio.Queue = asyncio.Queue()
        self.worker = asyncio.run_coroutine_threadsafe(self._worker(), self.loop)

    async def _worker(self):
        host = ChatHost()
        try:
            while True:
                job = await self.jobs.get()
                if job is None:
                    break
                func, future = job
                try:
                    future.set_result(await func(host))
                except Exception as e:
                    future.set_exception(e)
        finally:
            await host.cleanup()

    def submit(self, func: Callable[[ChatHost], Awaitable[Any]]) -> concurrent.futures.Future:
        """Queue func(host) to run on the worker task."""
        future: concurrent.futures.Future = concurrent.futures.Future()
        self.loop.call_soon_threadsafe(self.jobs.put_nowait, (func, future))
        return future

    def close(self):
        self.loop.call_soon_threadsafe(self.jobs.put_nowait, None)
        try:
            self.worker.result(timeout=15)
        except Exception:
            pass
        self.loop.call_soon_threadsafe(self.loop.stop)


runner = HostRunner()
atexit.register(runner.close)


async def respond(message: str, history: list):
    message = message.strip()
    if not message:
        yield "", history
        return

    history = history + [{"role": "user", "content": message}]
    yield "", history

    # Only the final answer is shown; text written before a tool call is
    # part of the process and is dropped, as are the tool calls themselves
    answer: list[str] = []

    def on_step(event: dict[str, Any]):
        if event["type"] == "text":
            answer.append(event["text"])
        elif event["type"] == "tool_call":
            answer.clear()

    try:
        await asyncio.wrap_future(runner.submit(lambda host: host.process_query(message, on_step)))
        content = "\n\n".join(answer) or "לא התקבלה תשובה."
    except Exception as e:
        content = f"⚠️ שגיאה: {e}"

    history.append({"role": "assistant", "content": content})
    yield "", history


async def reset():
    async def _reset(host: ChatHost):
        host.reset_conversation()

    await asyncio.wrap_future(runner.submit(_reset))
    return [], ""


with gr.Blocks(title="מזג אוויר - MCP") as demo:
    gr.Markdown("# 🌦️ סוכן מזג אוויר\nישראל (weather2day) וארה\"ב (NWS), דרך שרתי MCP", rtl=True)

    chatbot = gr.Chatbot(
        height=600,
        rtl=True,
        placeholder=PLACEHOLDER,
        buttons=["copy"],
        show_label=False,
    )

    with gr.Row():
        textbox = gr.Textbox(
            placeholder="כתבי שאלה ולחצי Enter...",
            rtl=True,
            show_label=False,
            scale=8,
            autofocus=True,
        )
        send = gr.Button("שליחה", variant="primary", scale=1)
        clear = gr.Button("🗑️ שיחה חדשה", scale=1)

    textbox.submit(respond, [textbox, chatbot], [textbox, chatbot])
    send.click(respond, [textbox, chatbot], [textbox, chatbot])
    clear.click(reset, None, [chatbot, textbox])


if __name__ == "__main__":
    # Connect to the MCP servers up front so problems show at startup
    runner.submit(lambda host: host.connect_mcp_clients()).result(timeout=60)
    demo.launch(inbrowser=True, theme=gr.themes.Soft(), css=CSS)
