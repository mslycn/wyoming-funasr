from wyoming.server import AsyncTcpServer

from .stt import FunASRSTT
from .info import create_describe


async def run_server(host: str, port: int):
    server = AsyncTcpServer(host, port)

    server.add_handler(create_describe())
    server.add_handler(FunASRSTT())

    await server.run()
