"""
  Server part for connections
"""

import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport
    #TODO


class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def create_protocol(self):
        return ClientProtocol()

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888,

        )

        print('Server has been started...')

        await coroutine.serve_forever()


process = Server()
asyncio.run(process.start())

# print(dir(process))
