"""
  Client side app with UI interface
"""

import asyncio
from asyncio import transports

from PySide2.QtWidgets import QMainWindow, QApplication
from asyncqt import QEventLoop

from interface import Ui_MainWindow


class ClientProtocol(asyncio.Protocol):
    transport: transports.Transport
    # client should be able to put all messages that return to us
    # attach client protocol with text fields
    window: 'Chat'

    def __init__(self, chat):
        self.window = chat

    def data_received(self, data: bytes):
        print(data)
        decoded = data.decode()
        self.window.plainTextEdit.appendPlainText(decoded)

    def connection_made(self, transport: transports.Transport):
        self.window.plainTextEdit.appendPlainText('Connection established successfully, enter your login')
        self.transport = transport

    def connection_lost(self, exception):
        self.window.plainTextEdit.appendPlainText('Connection has been lost')
    

class Chat(QMainWindow, Ui_MainWindow):
    protocol: ClientProtocol

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 'send' button handler
        self.pushButton.clicked.connect(self.send_message)

    def send_message(self):
        message = self.lineEdit.text()
        self.lineEdit.clear()
        # send encoded message through transport protocol
        self.protocol.transport.write(message.encode())

    def create_protocol(self):
        # attach window to client protocol
        self.protocol1 = ClientProtocol(self)
        return self.protocol1

    async def start(self):
        # show chat window
        self.show()

        loop = asyncio.get_running_loop()

        # '-await' no asynchronous needed here
        coroutine = loop.create_connection(
            self.create_protocol,
            "127.0.0.1",
            9898,
        )

        # client has only one connection, therefore just one coroutine with 1 sec timeout 
        # await asyncio.wait_for(coroutine, 1000)
        # app hangs with 1 sec
        await asyncio.wait_for(coroutine, 1000)


app = QApplication()
# since PyQT is not fully support asynchronous, we'll use module 'asyncqt'
# to switch between async server events and sync events from PyQT
loop = QEventLoop(app)

# set events stream and pass our loop
asyncio.set_event_loop(loop)

window = Chat()
x = ClientProtocol(window)
print(dir(x))
# create task in loop event
loop.create_task(window.start())
app.exec_()
loop.run_forever()
