from asyncio import Future
from typing  import Awaitable, Iterable, List, Optional, Set, Tuple
from enum    import IntEnum

from ircstates import Server, Emit
from irctokens import Line

from .params   import ConnectionParams, SASLParams, STSPolicy

class ITCPReader(object):
    async def read(self, byte_count: int):
        pass
class ITCPWriter(object):
    def write(self, data: bytes):
        pass
    async def drain(self):
        pass

class ITCPTransport(object):
    async def connect(self,
            hostname:   str,
            port:       int,
            tls:        bool,
            tls_verify: bool=True,
            bindhost:   Optional[str]=None
            ) -> Tuple[ITCPReader, ITCPWriter]:
        pass

class SendPriority(IntEnum):
    HIGH   = 0
    MEDIUM = 10
    LOW    = 20
    DEFAULT = MEDIUM

class SentLine(object):
    def __init__(self,
            id:       int,
            priority: int,
            line:     Line):
        self.id             = id
        self.priority       = priority
        self.line           = line
        self.future: Future = Future()

    def __lt__(self, other: "SentLine") -> bool:
        return self.priority < other.priority

class ICapability(object):
    def available(self, capabilities: Iterable[str]) -> Optional[str]:
        pass

    def match(self, capability: str) -> bool:
        pass

    def copy(self) -> "ICapability":
        pass

class IMatchResponse(object):
    def match(self, server: "IServer", line: Line) -> bool:
        pass
class IMatchResponseParam(object):
    def match(self, server: "IServer", arg: str) -> bool:
        pass

class IServer(Server):
    disconnected: bool
    params:       ConnectionParams
    desired_caps: Set[ICapability]

    def send_raw(self, line: str, priority=SendPriority.DEFAULT
            ) -> Awaitable[SentLine]:
        pass
    def send(self, line: Line, priority=SendPriority.DEFAULT
            ) -> Awaitable[SentLine]:
        pass

    def wait_for(self, response: IMatchResponse) -> Awaitable[Line]:
        pass

    def set_throttle(self, rate: int, time: float):
        pass

    async def connect(self,
            transport: ITCPTransport,
            params:    ConnectionParams):
        pass
    async def disconnect(self):
        pass

    async def line_read(self, line: Line):
        pass
    async def line_send(self, line: Line):
        pass
    def sts_policy(self, sts: STSPolicy):
        pass

    async def next_line(self) -> Optional[Tuple[Line, List[Emit]]]:
        pass

    def cap_agreed(self, capability: ICapability) -> bool:
        pass
    def cap_available(self, capability: ICapability) -> Optional[str]:
        pass

    async def sasl_auth(self, sasl: SASLParams) -> bool:
        pass

class IBot(object):
    def create_server(self, name: str) -> IServer:
        pass
    async def disconnected(self, server: IServer):
        pass

    async def disconnect(self, server: IServer):
        pass

    async def add_server(self, name: str, params: ConnectionParams) -> IServer:
        pass

    async def run(self):
        pass
