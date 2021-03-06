import asyncio
import anyio

from typing import Dict

from .server    import ConnectionParams, Server
from .transport import TCPTransport
from .interface import IBot, IServer

RECONNECT_DELAY = 10.0 # ten seconds reconnect

class Bot(IBot):
    def __init__(self):
        self.servers: Dict[str, Server] = {}
        self._server_queue: asyncio.Queue[Server] = asyncio.Queue()

    # methods designed to be overridden
    def create_server(self, name: str):
        return Server(self, name)
    async def disconnected(self, server: IServer):
        if (server.name in self.servers and
                server.disconnected):
            await asyncio.sleep(RECONNECT_DELAY)
            await self.add_server(server.name, server.params)
    # /methods designed to be overridden

    async def disconnect(self, server: IServer):
        await server.disconnect()
        del self.servers[server.name]

    async def add_server(self, name: str, params: ConnectionParams) -> Server:
        server = self.create_server(name)
        self.servers[name] = server
        await server.connect(TCPTransport(), params)
        await self._server_queue.put(server)
        return server

    async def _run_server(self, server: Server):
        async with anyio.create_task_group() as tg:
            async def _read():
                while not tg.cancel_scope.cancel_called:
                    both = await server.next_line()
                    if both is None:
                        break
                await tg.cancel_scope.cancel()

            async def _write():
                while not tg.cancel_scope.cancel_called:
                    lines = await server._write_lines()
                await tg.cancel_scope.cancel()

            await tg.spawn(_write)
            await tg.spawn(_read)

        await self.disconnected(server)

    async def run(self):
        async with anyio.create_task_group() as tg:
            while not tg.cancel_scope.cancel_called:
                server = await self._server_queue.get()
                await tg.spawn(self._run_server, server)
