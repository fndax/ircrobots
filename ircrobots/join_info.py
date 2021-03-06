from typing    import Dict, Iterable, List, Optional
from irctokens import build
from ircstates.numerics import *

from .contexts  import ServerContext
from .matching  import Response, ResponseOr, ParamAny, ParamFolded

class WHOContext(ServerContext):
    async def ensure(self, channel: str):
        folded = self.server.casefold(channel)

        if self.server.isupport.whox:
            await self.server.send(self.server.prepare_whox(channel))
        else:
            await self.server.send(build("WHO", [channel]))

        line = await self.server.wait_for(
            Response(RPL_ENDOFWHO, [ParamAny(), ParamFolded(folded)])
        )
