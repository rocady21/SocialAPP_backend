from flask_socketio import emit,send,SocketIO
from flask import request
socket_io = SocketIO(cors_allowed_origins="*")

@socket_io.on("connect")
def connected():
    emit("mensaje_servidor", {"mensaje": "El usuario está conectadoo"})

@socket_io.on("hola_mundo")
def hola_mundo():
    emit("respuesta_hola_mundo", {"mensaje": "¡Hola, mundo!"})


@socket_io.on("message")
def recive_message(data):
    print(str(data))

@socket_io.on("mostrar_mensaje_recibido")
def recive_message(data):
    emit("recive_message",{"mensaje":str(data)})