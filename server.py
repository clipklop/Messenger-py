"""
  Server side for connections
"""

import asyncio
from asyncio import transports


class ClientProtocol(asyncio.Protocol):
    login: str
    server: 'Server'
    transport: transports.Transport
    
    def __init__(self, server: 'Server'):
        self.server = server
        self.login = None

    def data_received(self, data: bytes):
        decoded = data.decode()
        print(decoded)

        if self.login is None:
            # login: User
            if decoded.startswith('login:'):
                temp_login = decoded.replace('login:','').replace('\r\n', '')
                
                # check if login is in use
                for user in self.server_clients:
                    if user.login == temp_login:
                        self.transport.write('Login has already in use')
                        self.transport.close()
                        return
                
                self.transport.write(
                    f'Welcome back, {self.login}'.encode()
                )
                self.send_history()
            else:
                self.send_message(decoded)
    
    def send_history(self):
        last_messages = self.server.messages[-10:]
        # encode every history message to correctly send it
        [self.transport.write(i.encode()) for i in last_messages]

    def send_message(self, message):
        format_string = f'<{self.login}> {message}'
        # save messages to servers list
        self.server.messages.append(format_string)

        encoded = format_string.encode()

        [client.transport.write(encoded) for client in self.server.clients if client.login != self.login]

    def connection_made(self, transport: transports.Transport):
        self.transport = transport
        self.server.clients.append(self)
        print('Connection established')
    
    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print('Connection has been lost')


class Server:
    clients: list
    messages: list

    def __init__(self):
        self.clients = []
        self.messages = []

    def create_protocol(self):
        return ClientProtocol(self)

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
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print('Server has been manually stopped')
