
from flask_socketio import SocketIO
socket_io = SocketIO(cors_allowed_origins="*")


@socket_io.on('connect')
def handle_connect():
    print('Client connected')
    socket_io.emit("response_data","cliente conectado")

@socket_io.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socket_io.on('message_to_server')
def handle_msg(data):
    print('Mensaje al servidor')
    print(data)
@socket_io.on("hola")
def handleHola(data):
    print(data,"data")